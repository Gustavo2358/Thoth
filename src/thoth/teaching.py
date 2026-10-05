from thoth import prompts
from thoth.contracts import TeachingDecision, Review, digest
from thoth.conversation import reference, context


def analyze(raw, turns, extraction, store, llm, sid, occurred_on):
    groups = store.teaching_groups()
    accepted, rejected, goals = [], [], []
    seen = set()
    for proposal in extraction.teaching:
        refs = [reference(raw, turns, ref.turn, ref.quote) for ref in proposal.refs]
        if not any(r['speaker'] == 'learner' for r in refs):
            rejected.append({'proposal': proposal.model_dump(), 'reason': 'No learner statement supports this teaching evidence'})
            continue
        identity = digest([sid, refs, proposal.instruction])
        if identity in seen:
            raise ValueError('Duplicate teaching evidence')
        seen.add(identity)
        decision = llm.call('teaching', prompts.TEACHING,
                            {'conversation': context(turns), 'proposal': proposal.model_dump(), 'groups': groups}, TeachingDecision)
        if decision.directive_id and decision.directive_id not in {g['id'] for g in groups}:
            raise ValueError('Teaching resolver selected an unknown directive')
        if decision.decision == 'reject':
            rejected.append({'proposal': proposal.model_dump(), 'decision': decision.model_dump()})
            continue
        did = decision.directive_id if decision.decision == 'same_directive' else 'TD-' + identity[:12] if decision.decision == 'new_directive' else None
        item = dict(id='TE-' + identity[:16], session_id=sid, occurred_on=occurred_on,
                    data=proposal.model_dump(), refs=refs, directive_id=did, decision=decision.model_dump())
        accepted.append(item)
        if did:
            group = next((g for g in groups if g['id'] == did), None)
            if group is None:
                groups.append(dict(id=did, instruction=proposal.instruction, evidence=[item]))
            else:
                group['evidence'].append(item)
    for proposal in extraction.goals:
        ref = reference(raw, turns, proposal.ref.turn, proposal.ref.quote, speaker='learner')
        review = llm.call('goal-review', prompts.GOAL_REVIEW,
                          {'conversation': context(turns), 'proposal': proposal.model_dump()}, Review)
        if review.decision == 'keep':
            goals.append(dict(text=proposal.text, ref=ref))
        else:
            rejected.append({'goal': proposal.model_dump(), 'review': review.model_dump()})
    return accepted, goals, rejected


def teaching_state(store):
    result = []
    for group in store.teaching_groups():
        evidence = group['evidence']
        explicit = any(e['data']['durable'] for e in evidence)
        # Reactions can support a hypothesis, never a declared optimal learning style.
        dates = {e['occurred_on'] for e in evidence}
        status = 'explicit' if explicit else 'inferred' if len(dates) >= 2 else 'tentative'
        result.append(dict(id=group['id'], instruction=group['instruction'], status=status,
                           rationale=evidence[-1]['data']['interpretation'],
                           evidence_ids=[e['id'] for e in evidence], dates=sorted(dates)))
    return {'directives': result, 'evidence': store.teaching_records()}
