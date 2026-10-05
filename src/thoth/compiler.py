"""Deterministic selection and bounded rendering. No new learner facts from prose synthesis."""
from __future__ import annotations

import hashlib
import re

from thoth.conversation import parse, reference
from thoth.engine import learner_state
from thoth.teaching import teaching_state


BASE = """# Your next English conversation

## Role and purpose
Be my conversational English teacher for spontaneous spoken production. Start a real conversation,
not a grammar lecture, writing exercise, pronunciation assessment or scripted test. Follow interesting
tangents and respond to meaning before form. The private priorities below guide opportunities;
do not announce a checklist or require a particular expression when an appropriate alternative works.

## Learner context
Continue from evidence in prior learning conversations. Treat emerging patterns and recent improvement
as hypotheses about observed production, not fixed weaknesses, mastery, or psychological traits.

## General teaching policy
These are general defaults, not inferred personal preferences:
- Let me attempt before showing a model whenever useful. Preserve flow; select only high-value feedback.
- After meaningful corrective feedback, invite another production attempt. Use a brief explanation or
  scaffold when helpful; later revisit the same communicative capability in a different situation.
- Accept valid alternatives and suitable registers. Optional stylistic changes are not errors.
- Distinguish immediate imitation, supported practice and later spontaneous use. A correct echo does
  not establish transfer. Give feedback after a meaningful turn, not at every small deviation.
- Revisit relevant earlier learning across sessions, a little at a time. Do not try to complete a plan
  when the conversation takes a productive direction. Conversation quality constrains all priorities.
- For observation and transfer, never supply or remind me of target wording before my attempt, name
  the form to produce, or read private evidence aloud. If no natural opportunity arises, let it go.

## Goals and conversation agenda
Use the goals below to choose meaningful topics. Goals lead the agenda; patterns must not monopolize
it. Invite me to choose a topic if no goal is recorded. Let me finish complex thoughts before feedback.
"""


def words(text):
    return set(re.findall(r'[a-z]{4,}', text.casefold())) - {'english', 'naturally', 'spoken', 'production', 'explain', 'learning', 'learner', 'conversation'}


def leaks_wording(block, members):
    # A mechanical last guard, not a semantic detector: do not let an accidentally
    # form-bearing communicative intent copy source/model wording into a protected probe.
    def normalized(text):
        return ' '.join(re.findall(r"[a-z']+", text.casefold()))
    content = ' ' + normalized(block) + ' '
    forms = [form for r in members for form in [r['observation'].learner_quote, *r['observation'].suggested_forms]]
    return any(len(normalized(form).split()) >= 2 and ' ' + normalized(form) + ' ' in content for form in forms)


def compile_prompt(store, policy):
    state = learner_state(store, policy)
    teaching = teaching_state(store)
    goals = store.goals()
    records = {r['id']: r for r in store.records()}
    sources = {s['id']: s for s in store.sources()}
    lines, omitted, selections = [BASE.rstrip()], [], []
    audit = {'policy': policy.model_dump(), 'sources': {s['id']: {'sha256': s['source_sha256'], 'date': s['occurred_on'],
              'path': f"sessions/{s['id']}/conversation.md"} for s in sources.values()},
             'goals': [], 'directives': [], 'patterns': selections, 'omitted': omitted,
             'product_policy': 'General oral-production defaults in compiler.BASE; not learner-specific evidence'}
    flexible = policy.prompt_chars - len(BASE) - 300
    goal_budget, directive_budget = min(1400, flexible // 3), min(1800, flexible // 3)
    audit['section_budgets'] = {'goals': goal_budget, 'directives': directive_budget, 'reserved_structure': 300}
    # Reserve room for instructions and learning strategy instead of filling the entire prompt with goals.
    def add(block, item, section_budget=None):
        size = len('\n\n'.join(lines + [block])) + 1
        # Reserve fixed headings/empty-state messages, so budget pressure never
        # requires chopping an instruction or failing after selection.
        if size + 300 > policy.prompt_chars or (section_budget is not None and len(block) > section_budget):
            omitted.append({**item, 'reason': 'budget; complete instruction omitted'})
            return False
        lines.append(block)
        return True
    used = 0
    for goal in goals:
        block = '- ' + goal['text']
        if add(block, {'kind': 'goal', 'id': goal['id']}, goal_budget - used):
            audit['goals'].append(goal)
            used += len(block)
    if not goals:
        lines.append('No explicit goals recorded yet; ask what I want to discuss today.')
    lines.append('## How to teach me — supported personal instructions')
    used = 0
    for d in sorted(teaching['directives'], key=lambda d: (d['status'] != 'explicit', d['id'])):
        if d['status'] == 'tentative':
            omitted.append({'kind': 'directive', 'id': d['id'], 'reason': 'single-date tentative evidence; not a persistent instruction'})
            continue
        block = '- ' + ('Explicit request: ' if d['status'] == 'explicit' else 'Tentative recurring hypothesis; check whether it helps: ') + d['instruction']
        if add(block, {'kind': 'directive', 'id': d['id']}, directive_budget - used):
            audit['directives'].append({**d, 'evidence': [e for e in teaching['evidence'] if e['id'] in d['evidence_ids']]})
            used += len(block)
    if not audit['directives']:
        lines.append('Follow the general policy and ask which feedback style I prefer today.'
                     if any(d['status'] != 'tentative' for d in teaching['directives'])
                     else 'No persistent personal teaching instruction is sufficiently supported yet.')
    goal_words = words(' '.join(g['text'] for g in goals))
    ranked = sorted(state['patterns'], key=lambda p: (
        p['stale'], -len(goal_words & words(p['label'] + ' ' + p['description'] + ' '.join(p['conversation_contexts']))),
        -int(p['last_seen'].replace('-', '')), -p['recent_difficulties'], -p['dates'], p['id']))
    counts = {'practice': 0, 'observe': 0, 'transfer': 0}
    lines.append('## Private learning intentions for this conversation')

    def refs_for(ids):
        refs = []
        for oid in ids:
            r = records[oid]
            o = r['observation']
            source = sources[o.session_id]
            turns = parse(source['raw'])
            refs.append({'observation_id': oid, 'session_id': o.session_id, 'date': r['occurred_on'],
                         'performance': o.performance, 'mode': o.production_mode, 'support': o.support,
                         'production': reference(source['raw'], turns, o.turn, o.source_excerpt, o.learner_quote, 'learner'),
                         'support_refs': [reference(source['raw'], turns, t, turns[t-1].text) for t in o.support_turns]})
        return refs

    for p in ranked:
        strategy = 'practice' if p['status'] == 'practice' else 'transfer' if p['status'] in {'recovery', 'recent_strength'} else 'observe'
        limit = getattr(policy, strategy + '_limit')
        if counts[strategy] >= limit:
            omitted.append({'kind': 'pattern', 'id': p['id'], 'reason': 'priority/section limit', 'strategy': strategy})
            continue
        members = [records[i] for i in p['evidence_ids']]
        # For protected probes render communicative purposes, never target forms, suggestions or quotes.
        intent = members[-1]['observation'].communicative_intent
        if strategy == 'practice':
            block = '### Practice: ' + p['label'] + '\nRecurring unassisted difficulty was observed on independent dates. Let me attempt; respond to meaning,\nthen give selective feedback, a useful short explanation/scaffold and another attempt. Later vary the\ncontext for the same communicative purpose. Accept any appropriate formulation.\nPurpose: ' + intent
            difficult = [r for r in members if r['observation'].performance == 'difficulty']
            positive = [r for r in members if r['observation'].performance == 'successful']
            rep = ([difficult[0]] if difficult else []) + ([positive[-1]] if positive else [])
            for r in rep:
                q = r['observation'].learner_quote
                if len(q) <= 200:
                    block += '\nPrivate evidence, do not read before attempt: ' + r['observation'].performance + ' (' + r['observation'].production_mode + ', ' + r['observation'].support + ') — ' + repr(q)
            block += '\nUse this purpose only if it fits the goal-led conversation; do not force an unrelated topic.'
        elif strategy == 'transfer':
            block = '### Test transfer: ' + intent + '\nRecent unassisted success suggests improvement in a previously observed capability; broader transfer\nremains untested. Create a different communicative situation, without reminding me of previous wording\nor supplying a model. Observe spontaneous production first. Do not automatically teach this again.'
        else:
            block = '### Observe if natural: ' + intent + '\nEvidence is emerging, incompletely sampled or old; do not declare a weakness. Create a natural\nopportunity without a target form or model, and collect successful as well as difficult production.\nDo not force the opportunity if the conversation goes elsewhere.'
        if strategy != 'practice' and leaks_wording(block, members):
            omitted.append({'kind': 'pattern', 'id': p['id'], 'reason': 'non-priming guard: intent contains evidence/model wording', 'strategy': strategy})
            continue
        if add(block, {'kind': 'pattern', 'id': p['id'], 'strategy': strategy}):
            counts[strategy] += 1
            selections.append({'id': p['id'], 'status': p['status'], 'strategy': strategy,
                               'goal_overlap_terms': sorted(goal_words & words(p['description'])), 'evidence': refs_for(p['evidence_ids'])})
    # One provisional observation can be sampled without declaring or materializing a Pattern.
    grouped = {p['root_id'] for p in ranked}
    for r in sorted(records.values(), key=lambda r: r['occurred_on'], reverse=True):
        if r['root_id'] in grouped:
            continue
        grouped.add(r['root_id'])
        if counts['observe'] >= policy.observe_limit or r['observation'].review.decision != 'keep':
            omitted.append({'kind': 'observation', 'id': r['id'], 'reason': 'uncertain evidence or observation limit'})
            continue
        block = '### Observe if natural: ' + r['observation'].communicative_intent + '\nOne provisional evidence group; no recurring weakness established. Let me attempt in a natural context\nwithout supplying wording first. Do not force this topic or prescribe a particular expression.'
        members = [x for x in records.values() if x['root_id'] == r['root_id']]
        if leaks_wording(block, members):
            omitted.append({'kind': 'observation', 'id': r['id'], 'reason': 'non-priming guard: intent contains evidence/model wording'})
            continue
        if add(block, {'kind': 'observation', 'id': r['id']}):
            counts['observe'] += 1
            selections.append({'id': r['root_id'], 'status': 'isolated', 'strategy': 'observe',
                               'evidence': refs_for([x['id'] for x in records.values() if x['root_id'] == r['root_id']])})
    if not selections:
        lines.append('No selected learning pattern yet. Follow my goals and interests, with the general teaching policy.')
    prompt = '\n\n'.join(lines) + '\n'
    if len(prompt) > policy.prompt_chars:
        raise ValueError('Prompt budget too small for essential teaching policy and section headings')
    audit.update(characters=len(prompt), sha256=hashlib.sha256(prompt.encode()).hexdigest(), selection_counts=counts)
    return prompt, audit
