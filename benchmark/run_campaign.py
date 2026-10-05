"""Exercise the production CLI + manual adapter. Gold is loaded only after all ingestions finish."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile

from thoth.artifacts import write_json
from thoth.cli import main
from thoth.storage import Store
from thoth.benchmark import score
from thoth.engine import learner_state
from thoth.pipeline import policy_from_file


def run(output, exchange):
    campaign = json.loads(Path('benchmark/campaign.json').read_text())
    pending = []
    output.mkdir(parents=True, exist_ok=True)
    for profile, sessions in campaign['profiles'].items():
        # Every invocation starts from empty state; cached answers resume work, never future evidence.
        with tempfile.TemporaryDirectory(prefix=f'.{profile}-', dir=output) as temporary:
            root = Path(temporary)
            status = 0
            for index, session in enumerate(sessions, 1):
                capture = io.StringIO()
                with redirect_stdout(capture), redirect_stderr(capture):
                    status = main(['--db', str(root/'learner.db'), '--artifacts', str(root/'current'),
                                   'ingest', str(Path('benchmark/conversations')/session['file']), '--date', session['date'],
                                   '--model', campaign['model'], '--exchange', str(exchange)])
                if status:
                    print(profile, session['file'], capture.getvalue().strip())
                    if status == 2:
                        pending.append(session['file'])
                        break
                    return status
                shutil.copytree(root/'current', root/f'after-{index:02d}', dirs_exist_ok=True)
            if status == 0:
                shutil.copytree(root, output/profile, dirs_exist_ok=True)
    if pending:
        print(f'{len(pending)} profiles awaiting internal LLM responses')
        return 2
    # Evaluate accepted source evidence and prompt audit properties, independently of requests.
    gold = json.loads(Path('benchmark/gold/campaign.json').read_text())
    rows, omissions, support_errors, preference_failures, continuity_failures, nonpriming_failures = [], [], [], [], [], []
    total_directives = 0
    teaching_errors, grouping = [], {}
    for profile, sessions in campaign['profiles'].items():
        root = output/profile
        with Store(root/'learner.db') as store:
            sources = {s['id']: s for s in store.sources()}
            group_gold = {}
            for session in sessions:
                file = session['file']
                raw = (Path('benchmark/conversations')/file).read_text()
                source = next(s for s in sources.values() if s['raw'] == raw)
                actual = [r['observation'] for r in store.records() if r['session_id']==source['id']]
                expected = gold['conversations'][file]
                expected_counts = Counter(tuple(o) for o in expected['observations'])
                actual_counts = Counter((o.turn,o.performance,o.production_mode,o.support) for o in actual)
                if expected_counts != actual_counts:
                    support_errors.append({'file':file,'expected':expected['observations'], 'actual':list(actual_counts.elements())})
                expected_turns = {o[0] for o in expected['observations']}
                for o in actual:
                    if o.turn not in expected_turns:
                        omissions.append({'file':file,'unexpected_turn':o.turn})
                    group_gold[o.id] = {'group':expected['groups'].get(o.learner_quote)}
                actual_teaching = json.loads(source['audit'])['teaching']
                expected_t = Counter(tuple(e) for e in expected['teaching'])
                actual_t = Counter((e['data']['refs'][0]['turn'],e['data']['kind'],e['data']['durable']) for e in actual_teaching)
                if expected_t != actual_t:
                    teaching_errors.append({'file':file,'expected':expected['teaching'],'actual':list(actual_t.elements())})
                rows.append({'file':file,'observations':len(actual),'teaching':len(json.loads(source['audit'])['teaching']),
                             'non_evidence_turns':expected['non_evidence_turns']})
            history, retrieval = [], []
            audits = {g['observation_id']:g for source in sources.values() for g in json.loads(source['audit'])['grouping']}
            for record in store.records():
                group = group_gold[record['id']]['group']
                existed = group is not None and any(group_gold[r['id']]['group']==group for r in history)
                candidates = audits[record['id']]['candidates']
                hit = existed and any(group_gold[e['id']]['group']==group for c in candidates for e in c['evidence'])
                retrieval.append({'same_existed':existed,'retrieval_hit':hit,'expected':None,
                                  'actual':record['resolution'].decision})
                history.append(record)
            grouping[profile] = score(store.records(),learner_state(store,policy_from_file()),group_gold,retrieval)
        for index, session in enumerate(sessions,1):
            audit=json.loads((root/f'after-{index:02d}'/'teacher-prompt.audit.json').read_text())
            prompt=(root/f'after-{index:02d}'/'teacher-prompt.md').read_text()
            rubric=gold['prompts'][session['file']]
            for text in rubric['include']:
                if text not in prompt: continuity_failures.append({'file':session['file'],'missing':text})
            for text in rubric['omit']:
                if text in prompt: preference_failures.append({'file':session['file'],'unsupported':text})
            for strategy in rubric['strategies']:
                if strategy not in [p['strategy'] for p in audit['patterns']]:
                    continuity_failures.append({'file':session['file'],'missing_strategy':strategy})
            for text in rubric['not_prime']:
                if text in prompt: nonpriming_failures.append({'file':session['file'],'leaked':text})
            total_directives += len(audit['directives'])
            supported = gold['supported_directives'][profile]
            for directive in audit['directives']:
                if directive['instruction'] not in supported:
                    preference_failures.append({'file':session['file'],'unsupported':directive['instruction']})
    failures=len(omissions)+len(support_errors)+len(teaching_errors)+len(preference_failures)+len(continuity_failures)+len(nonpriming_failures)
    failures += sum(g['pairwise']['false_merge_pairs']+g['pairwise']['false_split_pairs']+len(g['premature_patterns'])+len(g['missed_recurrences']) for g in grouping.values())
    result={'profiles':len(campaign['profiles']),'sessions':len(rows),'cases':rows,
            'unexpected_observations':omissions,'support_or_performance_failures':support_errors,
            'teaching_extraction_failures':teaching_errors, 'learner_grouping':grouping,
            'unsupported_teaching_preference_items':preference_failures,'prompt_directive_items_checked':total_directives,
            'unsupported_preference_rate':len(preference_failures)/total_directives if total_directives else None,
            'prompt_continuity_failures':continuity_failures,'non_priming_failures':nonpriming_failures,
            'controlled_gates_passed':failures==0,
            'limitations':'Same assistant authored conversations, semantic responses and gold. Saved-response replay is not independent LLM qualification. No real conversations or learning gains measured.'}
    write_json(output/'result.json',result)
    print(json.dumps(result,indent=2))
    return 0 if failures==0 else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('reports/continuity'))
    parser.add_argument('--exchange',type=Path,default=Path('reports/continuity/exchange'))
    args=parser.parse_args()
    sys.exit(run(args.output,args.exchange))
