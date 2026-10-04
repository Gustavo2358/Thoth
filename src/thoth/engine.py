from __future__ import annotations

from collections import defaultdict

from scipy.stats import beta

from thoth.contracts import Mode, Observation, TAXONOMY

ENGINE_VERSION = "engine-1"


def posterior(successes: int, failures: int) -> dict:
    if successes < 0 or failures < 0:
        raise ValueError("Counts must be nonnegative")
    a, b = successes + 1, failures + 1
    interval = beta.ppf([0.025, 0.975], a, b)
    return {"model": "Beta(1,1) prior + independent Bernoulli attempts",
            "successes": successes, "failures": failures, "attempts": successes + failures,
            "alpha": a, "beta": b, "posterior_mean": a / (a + b),
            "credible_interval_95": [float(x) for x in interval]}


def is_attempt(o: Observation) -> bool:
    return (o.verifier_decision == "supported" and o.issue_kind in {"grammar", "none"}
            and o.evidence_type.value in {"successful_use", "explicit_correction", "inferred_error"}
            and o.construction != "unclassified" and o.outcome.value in {"correct", "incorrect"})


def trend(observations: list[Observation], sessions: dict) -> dict:
    by_session = defaultdict(list)
    for o in observations:
        if is_attempt(o) and o.production_mode.value == "spontaneous":
            by_session[o.session_id].append(o)
    ordered = sorted(by_session, key=lambda sid: (sessions[sid]["occurred_on"], sid))
    series = [{"session_id": sid, "date": sessions[sid]["occurred_on"],
               "successes": sum(o.outcome.value == "correct" for o in by_session[sid]),
               "attempts": len(by_session[sid])} for sid in ordered]
    result = {"label": "insufficient_data", "rule": "At least 4 distinct dates, 2 sessions and 5 spontaneous attempts in each half; delta >= 0.20 improving, <= -0.20 declining; otherwise stable. Descriptive, not a significance test.",
              "session_series": series}
    if len(ordered) < 4 or len({sessions[s]["occurred_on"] for s in ordered}) < 4:
        return result
    midpoint = len(series) // 2
    early, late = series[:midpoint], series[midpoint:]
    if min(sum(x["attempts"] for x in early), sum(x["attempts"] for x in late)) < 5:
        return result
    rate = lambda xs: sum(x["successes"] for x in xs) / sum(x["attempts"] for x in xs)
    delta = rate(late) - rate(early)
    return {**result, "label": "improving" if delta >= .20 else "declining" if delta <= -.20 else "stable",
            "early_accuracy": rate(early), "recent_accuracy": rate(late), "delta": delta}


def aggregate(observations: list[Observation], sessions: dict[str, dict]) -> dict:
    # Identical inputs produce identical outputs, regardless of order. No clock or LLM.
    unique = {o.id: o for o in observations}
    if len(unique) != len(observations):
        raise ValueError("Duplicate observation IDs in state input")
    groups = defaultdict(list)
    for o in observations:
        if o.session_id not in sessions:
            raise ValueError("Observation refers to missing session metadata")
        groups[o.construction].append(o)
    constructions = {}
    for family, group in sorted(groups.items()):
        ordered = sorted(group, key=lambda o: (sessions[o.session_id]["occurred_on"], o.session_id, o.source_start, o.id))
        modes = {}
        for mode in Mode:
            attempts = [o for o in ordered if is_attempt(o) and o.production_mode == mode]
            successes = sum(o.outcome.value == "correct" for o in attempts)
            modes[mode.value] = posterior(successes, len(attempts) - successes)
        features = {feature: sum(is_attempt(o) and o.feature == feature for o in ordered)
                    for feature in ("affirmative", "negative", "question", "unknown")}
        last_three = {sid for sid in sorted({o.session_id for o in group},
                     key=lambda sid: (sessions[sid]["occurred_on"], sid))[-3:]}
        recent_failures = [o for o in ordered if is_attempt(o) and o.production_mode.value == "spontaneous"
                           and o.outcome.value == "incorrect" and o.session_id in last_three]
        sp = modes["spontaneous"]
        interpretation = ("Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven."
                          if sp["failures"] >= 2 and len({o.session_id for o in recent_failures}) >= 2
                          else "Observed difficulty requires more independent sessions." if sp["failures"]
                          else "Observed successes in these contexts; transfer remains untested." if sp["successes"]
                          else "Insufficient spontaneous attempt evidence.")
        constructions[family] = {
            "label": TAXONOMY[family], "modes": modes, "opportunities": sum(o.evidence_type.value == "opportunity" for o in group),
            "self_corrections": sum(o.evidence_type.value == "self_correction" for o in group),
            "uncertain_observations": sum(o.outcome.value == "uncertain" for o in group),
            "sessions_observed": len({o.session_id for o in group}),
            "last_seen": sessions[ordered[-1].session_id]["occurred_on"],
            "support_score_counts": {str(score): sum(o.raw_support_score == score for o in group) for score in range(1, 5)},
            "pipeline_ids": sorted({o.pipeline_id for o in group}), "features": features,
            "trend": trend(ordered, sessions), "recent_spontaneous_failures": len(recent_failures),
            "interpretation": interpretation,
            "unknowns": [f"Insufficient evidence for {f} forms (fewer than 3 attempts)." for f in ("negative", "question") if features[f] < 3]
                        + (["Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence."] if sp["attempts"] < 5 else []),
            "evidence_ids": [o.id for o in ordered], "recent_evidence_ids": [o.id for o in ordered[-5:]],
        }
    return {"engine_version": ENGINE_VERSION, "sessions": len(sessions), "observations": len(observations),
            "assumptions": ["Only supported grammatical attempts enter accuracy counts.",
                            "Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.",
                            "Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event."],
            "constructions": constructions}


def lesson_targets(state: dict) -> dict:
    primary, collect, strengths = [], [], []
    for family, entry in state["constructions"].items():
        if family == "unclassified":
            continue
        sp = entry["modes"]["spontaneous"]
        if sp["attempts"] >= 3 and entry["sessions_observed"] >= 2 and entry["recent_spontaneous_failures"] >= 2:
            primary.append((family, entry))
        elif sp["attempts"] < 5 or sp["credible_interval_95"][1] - sp["credible_interval_95"][0] > .5:
            collect.append((family, entry))
        if sp["attempts"] >= 5 and sp["credible_interval_95"][0] >= .6:
            strengths.append(family)
    primary.sort(key=lambda pair: (-pair[1]["recent_spontaneous_failures"], -pair[1]["modes"]["spontaneous"]["failures"], pair[0]))
    collect.sort(key=lambda pair: (pair[1]["modes"]["spontaneous"]["attempts"], -pair[1]["opportunities"], pair[0]))
    return {"primary": [f for f, _ in primary[:2]], "observation": [f for f, _ in collect[:2]],
            "strengths": sorted(strengths),
            "selection_rule": "Practice: >=3 spontaneous attempts across >=2 sessions and >=2 spontaneous failures in the last 3 observed sessions; rank by recent failures. Collect: <5 attempts or 95% interval width >0.5. Strength: >=5 attempts and lower credible bound >=0.6."}
