import json
from pathlib import Path
import sqlite3

import numpy as np
import pytest
from pydantic import ValidationError

from thoth.compiler import compile_prompt, leaks_wording
from thoth.contracts import Evidence, Extraction, TeachingEvidence, TeachingDecision, Review, Policy
from thoth.conversation import parse, reference
from thoth.pipeline import ingest, reprocess, policy_from_file
from thoth.storage import Store
from thoth.teaching import teaching_state
from thoth.cli import main
from thoth.llm import ManualChatGPTAdapter, PendingResponse
from test_core import add, fixture, decision

POLICY = policy_from_file()


@pytest.mark.parametrize('raw', [
    'Unlabelled transcript', '## User\nHello',
    '## User\nHello\n## System\nUnknown\n## Assistant\nHi',
    'Unlabelled content\n## User\nHello\n## Assistant\nHi',
    '## User\n\n## Assistant\nHi',
    '## User\n```\n## Assistant\nHi',
])
def test_parser_refuses_ambiguous_roles(raw):
    with pytest.raises(ValueError): parse(raw)


def test_parser_aliases_fences_crlf_unicode_and_repeated_quotes():
    raw = '# Export\r\n\r\n## LEARNER\r\n🎙️ Hello\r\n```md\r\n## Assistant\r\n```\r\n\r\n## Teacher\r\nHello\r\n\r\n## User\r\nHello\r\n'
    turns = parse(raw)
    assert [t.speaker for t in turns] == ['learner','teacher','learner']
    ref=reference(raw,turns,3,'Hello',speaker='learner')
    assert raw[ref['source_start']:ref['source_end']]=='Hello'
    assert ref['source_line_start']==13
    with pytest.raises(ValueError,match='learner'):
        reference(raw,turns,2,'Hello',speaker='learner')
    with pytest.raises(ValueError): reference(raw,turns,99,'Hello')


@pytest.mark.parametrize('support,mode,turns', [
    ('immediate_repetition','spontaneous',[1]),
    ('model_phrase_available','prompted',[1]),
    ('partial_scaffold','spontaneous',[1]),
    ('no_support','spontaneous',[1]),
    ('immediate_repetition','controlled',[]),
    ('contextual_prompt','prompted',[2]),
])
def test_support_schema_blocks_false_spontaneous_success(support,mode,turns):
    _,o=fixture(1)
    data=o.model_dump(exclude={'id','session_id','source_start','source_end','source_line_start','source_line_end','review'})
    with pytest.raises(ValidationError): Evidence.model_validate({**data,'support':support,'production_mode':mode,'support_turns':turns})


class Embedder:
    model='test'
    metadata={}
    def embed(self,texts): return [np.array([1.,0.],dtype='<f4') for _ in texts]


class TeachingLLM:
    trace=[]
    def __init__(self,proposal,choice='new_directive'):
        self.proposal,self.choice=proposal,choice
    def metadata(self):return {'model':'test'}
    def call(self,stage,prompt,data,contract):
        if stage=='extract':return Extraction(observations=[],teaching=[self.proposal],goals=[])
        if stage=='teaching':
            return TeachingDecision(decision=self.choice,directive_id=data['groups'][0]['id'] if self.choice=='same_directive' else None,reason='Test semantic decision')
        raise AssertionError(stage)


def teach(turn,quote,durable=False):
    return TeachingEvidence(refs=[{'turn':turn,'quote':quote}],kind='explicit_preference' if durable else 'situational_request',
                            durable=durable,instruction='Explain meaningful reformulations.',interpretation='Learner asks for reasons.')


def test_teacher_claim_cannot_supply_a_learner_preference():
    raw='## Assistant\nYou prefer grammar explanations.\n## User\nWhat about the project?\n'
    with Store(':memory:') as s:
        ingest(raw,'2026-01-01',s,Embedder(),TeachingLLM(teach(1,'You prefer grammar explanations.',True)),POLICY)
        assert teaching_state(s)['directives']==[]
        audit=json.loads(s.sources()[0]['audit'])
        assert audit['teaching_rejected'][0]['reason'].startswith('No learner')


def test_local_request_stays_tentative_explicit_directive_persists_and_dates_count():
    with Store(':memory:') as s:
        raw='## User\nCan you explain this change?\n## Assistant\nHere is why.\n'
        ingest(raw,'2026-01-01',s,Embedder(),TeachingLLM(teach(1,'Can you explain this change?')),POLICY)
        assert teaching_state(s)['directives'][0]['status']=='tentative'
        p,a=compile_prompt(s,POLICY)
        assert not a['directives']
        # More requests on the same date cannot promote an inference.
        raw2='# Another conversation\n'+raw
        ingest(raw2,'2026-01-01',s,Embedder(),TeachingLLM(teach(1,'Can you explain this change?'),'same_directive'),POLICY)
        assert teaching_state(s)['directives'][0]['status']=='tentative'
        raw3='# Later conversation\n'+raw
        ingest(raw3,'2026-01-08',s,Embedder(),TeachingLLM(teach(1,'Can you explain this change?'),'same_directive'),POLICY)
        assert teaching_state(s)['directives'][0]['status']=='inferred'
        assert 'Tentative recurring hypothesis' in compile_prompt(s,POLICY)[0]
    with Store(':memory:') as s:
        raw='## User\nPlease always explain why you changed my wording.\n## Assistant\nOkay.\n'
        ingest(raw,'2026-01-01',s,Embedder(),TeachingLLM(teach(1,'Please always explain why you changed my wording.',True)),POLICY)
        assert teaching_state(s)['directives'][0]['status']=='explicit'
        assert compile_prompt(s,POLICY)[1]['directives'][0]['evidence'][0]['refs'][0]['speaker']=='learner'


def test_one_positive_reaction_cannot_claim_durability():
    with pytest.raises(ValidationError):
        TeachingEvidence(refs=[{'turn':1,'quote':'That helped.'}],kind='intervention_response',durable=True,
                         instruction='Always use this method.',interpretation='Test')


def test_goals_explicit_simple_persisted_and_not_errors(tmp_path):
    with Store(tmp_path/'learner.db') as s:
        with s.db:
            gid=s.add_goal('Explain technical design trade-offs naturally')
            assert s.add_goal('  Explain technical design trade-offs naturally  ')==gid
        prompt,audit=compile_prompt(s,POLICY)
        assert 'Explain technical design trade-offs naturally' in prompt
        assert len(audit['goals'])==1 and s.records()==[]
    with Store(tmp_path/'learner.db') as s:
        assert s.goals()[0]['text']=='Explain technical design trade-offs naturally'


def test_controlled_success_does_not_trigger_recovery_but_unassisted_use_does():
    with Store(':memory:') as s:
        add(s,1,1)
        add(s,2,7,root='OBS-1')
        add(s,3,14,root='OBS-1',mode='controlled',performance='successful')
        prompt,a=compile_prompt(s,POLICY)
        assert a['patterns'][0]['strategy']=='practice'
        add(s,4,21,root='OBS-1',performance='successful')
        prompt,a=compile_prompt(s,POLICY)
        assert a['patterns'][0]['strategy']=='transfer'
        assert 'I agree.' not in prompt and 'I am agree' not in prompt
        assert a['patterns'][0]['evidence'][0]['production']['quote']=='I am agree with that.'
        assert any(e['support_refs'] for e in a['patterns'][0]['evidence'])


def test_old_pattern_returns_to_observation_instead_of_eternal_practice():
    with Store(':memory:') as s:
        add(s,1,1);add(s,2,7,root='OBS-1');add(s,3,14,root='OBS-1')
        raw='## User\nA different topic.\n## Assistant\nOkay.\n'
        s.commit_session(raw,'2026-03-01',[],{}, {},POLICY)
        prompt,a=compile_prompt(s,POLICY)
        assert a['patterns'][0]['strategy']=='observe'
        assert 'Recurring unassisted difficulty' not in prompt


def test_budget_omits_whole_items_preserves_goals_strategy_and_audit():
    with Store(':memory:') as s:
        add(s,1,1);add(s,2,7,root='OBS-1');add(s,3,14,root='OBS-1')
        with s.db:
            for n in range(30):s.add_goal(f'Goal {n}: discuss software architecture and reasoning ' + 'details '*40)
        small=POLICY.model_copy(update={'prompt_chars':4000})
        prompt,a=compile_prompt(s,small)
        assert len(prompt)<=4000
        assert a['omitted'] and a['goals'] and a['patterns']
        for item in a['omitted']:
            if item['kind']=='goal':
                goal=next(g for g in s.goals() if g['id']==item['id'])
                assert goal['text'] not in prompt
        assert prompt.endswith('\n') and 'Later vary the' in prompt


def test_nonpriming_guard_detects_wording_in_an_incorrect_intent():
    _,o=fixture(1)
    assert leaks_wording('Ask the learner to say I agree.', [{'observation':o}])
    assert not leaks_wording('Discuss a view and let the learner attempt.', [{'observation':o}])


def test_goals_rank_relevant_patterns_within_a_small_practice_limit():
    with Store(':memory:') as s:
        add(s,1,1);add(s,2,7,root='OBS-1')
        add(s,3,7);add(s,4,14,root='OBS-3')
        with s.db:
            s.add_goal('Discuss software architecture')
            s.db.execute("UPDATE patterns SET label='Explaining software architecture',description='Explaining architecture' WHERE root_id='OBS-1'")
            s.db.execute("UPDATE patterns SET label='A medication routine',description='Conventional medication verbs' WHERE root_id='OBS-3'")
        p,a=compile_prompt(s,POLICY.model_copy(update={'practice_limit':1}))
        assert a['patterns'][0]['id']=='PAT-1'
        assert any(x['id']=='PAT-3' and x['reason']=='priority/section limit' for x in a['omitted'])


def test_pending_reprocessing_leaves_source_state_and_manual_goals_intact():
    with Store(':memory:') as s:
        add(s,1,1)
        with s.db:s.add_goal('Explain technical reasoning')
        before=s.sources(),s.goals(),s.records()[0]['id']
        class Waiting:
            def call(self,*a):raise PendingResponse('missing')
        with pytest.raises(PendingResponse):reprocess(s,Embedder(),Waiting(),POLICY)
        assert (s.sources(),s.goals(),s.records()[0]['id'])==before
        with pytest.raises(sqlite3.IntegrityError):s.db.execute('DELETE FROM sessions')


def test_real_cli_longitudinal_replay_provenance_and_idempotency(tmp_path,capsys):
    base=['--db',str(tmp_path/'learner.db'),'--artifacts',str(tmp_path/'artifacts')]
    model='Codex / model of this conversation (operator declaration)'
    for n in (1,2,3):
        args=base+['ingest',f'examples/session-0{n}.md','--date',f'2026-03-{(n-1)*7+1:02d}',
                   '--model',model,'--exchange','reports/continuity/exchange']
        assert main(args)==0
        if n==1:
            audit=json.loads((tmp_path/'artifacts/teacher-prompt.audit.json').read_text())
            assert not any(p['strategy']=='transfer' for p in audit['patterns'])
        if n==2:
            audit=json.loads((tmp_path/'artifacts/teacher-prompt.audit.json').read_text())
            assert {p['strategy'] for p in audit['patterns']}=={'practice','transfer'}
    initial=(tmp_path/'artifacts/teacher-prompt.md').read_bytes()
    assert main(args)==0
    with Store(tmp_path/'learner.db') as s:
        assert len(s.sources())==3 and len(s.records())==9
        for src in s.sources():
            assert (tmp_path/'artifacts/sessions'/src['id']/'conversation.md').read_bytes()==src['raw'].encode()
    assert main(args+['--reprocess'])==0
    assert (tmp_path/'artifacts/teacher-prompt.md').read_bytes()==initial
    with Store(tmp_path/'learner.db') as s:
        assert len(s.records())==9
    assert main(base+['prepare'])==0
    assert 'Your next English conversation' in capsys.readouterr().out
