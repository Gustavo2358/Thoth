from __future__ import annotations

from collections import defaultdict

from scipy.stats import beta

from thoth.contracts import Mode, Observation, TAXONOMY

ENGINE_VERSION = "engine-2"


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
    # Keep reports from the same date in the same half. Multiple reports are
    # not additional independent dates and must not move the temporal boundary.
    dates = sorted({x["date"] for x in series})
    early_dates = set(dates[:len(dates) // 2])
    early, late = [x for x in series if x["date"] in early_dates], [x for x in series if x["date"] not in early_dates]
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
        spontaneous = [o for o in ordered if is_attempt(o) and o.production_mode.value == "spontaneous"]
        spontaneous_dates = sorted({sessions[o.session_id]["occurred_on"] for o in spontaneous})
        last_three_dates = set(spontaneous_dates[-3:])
        recent_failures = [o for o in spontaneous if o.outcome.value == "incorrect"
                           and sessions[o.session_id]["occurred_on"] in last_three_dates]
        failure_dates = sorted({sessions[o.session_id]["occurred_on"] for o in recent_failures})
        spontaneous_features = {feature: sum(o.feature == feature for o in spontaneous)
                                for feature in ("affirmative", "negative", "question", "unknown")}
        sp = modes["spontaneous"]
        guided_attempts = modes["prompted"]["attempts"] + modes["controlled"]["attempts"]
        guided_successes = modes["prompted"]["successes"] + modes["controlled"]["successes"]
        spontaneous_rate = sp["successes"] / sp["attempts"] if sp["attempts"] else None
        guided_rate = guided_successes / guided_attempts if guided_attempts else None
        gap = (sp["attempts"] >= 3 and guided_attempts >= 5
               and guided_rate - spontaneous_rate >= .30)
        interpretation = ("Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven."
                          if len(failure_dates) >= 2
                          else "Errors concentrated on one recent date; collect more independent spontaneous evidence." if recent_failures
                          else "Historical errors; no failures in the last three observed spontaneous-attempt dates. Transfer and mastery remain untested." if sp["failures"]
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
            "spontaneous_features": spontaneous_features, "spontaneous_attempt_dates": spontaneous_dates,
            "recent_failure_dates": failure_dates,
            "practice_evidence_ids": [o.id for o in recent_failures],
            "mode_gap": {"observed": bool(gap), "spontaneous_accuracy": spontaneous_rate,
                         "guided_accuracy": guided_rate, "guided_attempts": guided_attempts,
                         "interpretation": ("Prompted/controlled successes exceed spontaneous accuracy in the observed contexts. Task and context differences may explain this; no retrieval diagnosis."
                                            if gap else "Insufficient evidence of a prompted/controlled versus spontaneous gap."),
                         "rule": ">=3 spontaneous and >=5 guided attempts; observed accuracy gap >=0.30. Descriptive, not causal."},
            "trend": trend(ordered, sessions), "recent_spontaneous_failures": len(recent_failures),
            "interpretation": interpretation,
            "unknowns": [f"Insufficient evidence for spontaneous {f} forms (fewer than 3 attempts)." for f in ("negative", "question") if spontaneous_features[f] < 3]
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
        if sp["attempts"] >= 3 and len(entry["recent_failure_dates"]) >= 2:
            primary.append((family, entry))
        elif (sp["attempts"] < 5 or sp["credible_interval_95"][1] - sp["credible_interval_95"][0] > .5
              or len(entry["spontaneous_attempt_dates"]) < 2
              or any(entry["spontaneous_features"][form] < 3 for form in ("negative", "question"))):
            collect.append((family, entry))
        if (sp["attempts"] >= 5 and sp["credible_interval_95"][0] >= .6
                and len(entry["spontaneous_attempt_dates"]) >= 2
                and entry["recent_spontaneous_failures"] == 0):
            strengths.append(family)
    primary.sort(key=lambda pair: (-pair[1]["recent_spontaneous_failures"], -pair[1]["modes"]["spontaneous"]["failures"], pair[0]))
    collect.sort(key=lambda pair: (pair[1]["modes"]["spontaneous"]["attempts"], -pair[1]["opportunities"], pair[0]))
    return {"primary": [f for f, _ in primary[:2]], "observation": [f for f, _ in collect[:2]],
            "strengths": sorted(strengths),
            "selection_rule": "Practice: >=3 spontaneous attempts and failures on >=2 distinct dates among the last 3 spontaneous-attempt dates; rank by recent failures. Controlled practice and opportunities do not erase this window. Collect: <5 attempts, 95% interval width >0.5, fewer than 2 spontaneous dates, or missing spontaneous negative/question coverage (<3 per form). Strength: >=5 attempts, >=2 spontaneous dates, lower credible bound >=0.6, and no failures in that recent window. Recency is relative to observed attempts, not a calendar expiry; confirm old evidence in a new conversation."}
