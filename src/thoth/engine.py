from __future__ import annotations

from collections import defaultdict
import json
from datetime import date


def counted(o):
    return o.review.decision == "keep" and o.evidence_type in {"observed_use", "correction"} and o.performance != "uncertain"


def learner_state(store, policy):
    records = store.records()
    groups = defaultdict(list)
    for r in records:
        groups[r["root_id"]].append(r)
    result = []
    for root, pattern in store.patterns().items():
        members = groups[root]
        by_mode = {mode: {outcome: sum(r["observation"].production_mode == mode
                                      and r["observation"].performance == outcome
                                      and (outcome == "uncertain" or counted(r["observation"])) for r in members)
                          for outcome in ("successful", "difficulty", "uncertain")}
                   for mode in ("spontaneous", "prompted", "controlled", "unknown")}
        sp = [r for r in members if counted(r["observation"]) and r["observation"].production_mode == "spontaneous" and r["observation"].support == "no_support"]
        attempt_dates = sorted({r["occurred_on"] for r in sp})
        recent = [r for r in sp if r["occurred_on"] in attempt_dates[-3:]]
        failures = [r for r in recent if r["observation"].performance == "difficulty"]
        failure_dates = {r["occurred_on"] for r in failures}
        recent_attempts = [r for r in sp if r["occurred_on"] in attempt_dates[-policy.recovery_dates:]]
        positive_dates = {r["occurred_on"] for r in recent_attempts if r["observation"].performance == "successful"}
        recent_positive = len(positive_dates) >= policy.recovery_dates and not any(r["observation"].performance == "difficulty" for r in recent_attempts)
        all_dates = {r["occurred_on"] for r in members}
        practice = len(all_dates) >= policy.practice_dates and len(failure_dates) >= 2 and not recent_positive
        historical_difficulty = by_mode["spontaneous"]["difficulty"] > 0
        status = "recovery" if recent_positive and historical_difficulty else "recent_strength" if recent_positive else "practice" if practice else "collect"
        sources = store.sources()
        last_seen = max(r['occurred_on'] for r in members)
        intervening = len({s['occurred_on'] for s in sources if s['occurred_on'] > last_seen})
        stale = intervening >= policy.stale_dates or (date.fromisoformat(sources[-1]['occurred_on']) - date.fromisoformat(last_seen)).days >= policy.stale_days
        if stale:
            status = 'collect'
        interpretation = ("Previously difficult; recent spontaneous successes suggest recovery. Transfer remains untested."
                          if status == "recovery" else "Recent spontaneous successes in observed contexts; broader transfer remains untested."
                          if status == "recent_strength" else "Recurring spontaneous difficulties on independent dates; cause is not directly observed."
                          if status == "practice" else "Emerging or incompletely sampled pattern; collect more independent spontaneous evidence.")
        opportunities = sum(r["observation"].evidence_type == "opportunity" for r in members)
        repairs = sum(r["observation"].evidence_type == "self_correction" for r in members)
        guided_successes = by_mode["prompted"]["successful"] + by_mode["controlled"]["successful"]
        mode_note = ("Guided successes coexist with spontaneous difficulties; availability may differ by task, but retrieval cause is unproven."
                     if guided_successes and by_mode["spontaneous"]["difficulty"] else "Guided and spontaneous evidence remain separate.")
        result.append(dict(**{k: v for k, v in pattern.items() if k != "contexts"}, conversation_contexts=json.loads(pattern["contexts"]),
                           observations=len(members), sessions=len({r["session_id"] for r in members}),
                           dates=len(all_dates), modes=by_mode, opportunities=opportunities, self_corrections=repairs,
                           status=status, interpretation=interpretation, mode_note=mode_note,
                           last_seen=last_seen, stale=stale,
                           recent_successes=sum(r["observation"].performance == "successful" for r in recent),
                           recent_difficulties=len(failures), evidence_ids=[r["id"] for r in members],
                           practice_evidence_ids=[r["id"] for r in failures],
                           unknowns=["Transfer to new topics and registers is untested.",
                                     "Opportunities do not prove avoidance; L1 transfer and retrieval causes remain hypotheses."]
                                    + (["Fewer than two dates with spontaneous attempts."] if len(attempt_dates) < 2 else [])))
    result.sort(key=lambda p: (-p["recent_difficulties"], -p["dates"], p["id"]))
    return {"sessions": len(store.sources()), "observations": len(records), "patterns": result,
            "isolated": [{"id": r["id"], "dimension": r["observation"].learning_dimension,
                          "performance": r["observation"].performance, "reason": r["resolution"].reason}
                         for root, members in groups.items() if root not in store.patterns() for r in members],
            "assumptions": ["Counts describe selected conversation evidence, not mastery or a representative proficiency score.",
                            "Repeated conversations on one date do not establish longitudinal recurrence.",
                            "Pattern descriptions and causal interpretations are model hypotheses; quotes and memberships are auditable."]}
