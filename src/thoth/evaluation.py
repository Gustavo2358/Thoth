from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from thoth.contracts import Proposal
from thoth.provenance import normalized

MATCH_FIELDS = ("learner_start", "learner_utterance", "construction", "outcome", "production_mode", "evidence_type", "issue_kind", "feature", "corrected_form")


def match_key(value: dict) -> tuple:
    return tuple(normalized(value[f]) if f in {"learner_utterance", "corrected_form"} and value.get(f) is not None
                 else value.get(f) for f in MATCH_FIELDS)


def ratios(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"tp": tp, "false_positives": fp, "false_negatives": fn, "precision": precision, "recall": recall, "f1": f1}


def score_session(predictions: list[dict], gold: list[dict]) -> tuple[dict, list[bool]]:
    remaining = Counter(match_key(g) for g in gold)
    correct = []
    for p in predictions:
        k = match_key(p)
        supported = remaining[k] > 0
        correct.append(supported)
        if supported:
            remaining[k] -= 1
    tp = sum(correct)
    return ratios(tp, len(predictions) - tp, sum(remaining.values())), correct


def group_metrics(records: list[dict], field: str) -> dict:
    groups = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for record in records:
        predicted = record["predictions"]
        for value in {x[field] for x in predicted + record["gold"]}:
            metrics, _ = score_session([p for p in predicted if p[field] == value], [g for g in record["gold"] if g[field] == value])
            for target, source in (("tp", "tp"), ("fp", "false_positives"), ("fn", "false_negatives")):
                groups[value][target] += metrics[source]
    return {value: ratios(**counts) for value, counts in sorted(groups.items())}


def evaluate(records: list[dict]) -> dict:
    tp = fp = fn = hallucinated = rejected_provenance = negative_errors = negative_blocks = 0
    uncertainty = predictions = gold_count = 0
    confusion, failures, categories = Counter(), [], defaultdict(list)
    family_accuracy = defaultdict(lambda: {"aligned": 0, "correct_outcome": 0})
    attempt_tp = attempt_fp = attempt_fn = 0
    for record in records:
        if record.get("status") == "pending":
            continue
        metrics, correctness = score_session(record["predictions"], record["gold"])
        record["correctness"] = correctness
        tp += metrics["tp"]
        fp += metrics["false_positives"]
        fn += metrics["false_negatives"]
        predictions += len(record["predictions"])
        gold_count += len(record["gold"])
        uncertainty += sum(p["outcome"] == "uncertain" for p in record["predictions"])
        hallucinated += record["accepted_invalid_provenance"]
        rejected_provenance += record["rejected_provenance"]
        attempts = lambda items: [p for p in items if p["outcome"] in {"correct", "incorrect"} and p["issue_kind"] in {"grammar", "none"} and p["evidence_type"] not in {"opportunity", "self_correction", "other"}]
        a_metrics, _ = score_session(attempts(record["predictions"]), attempts(record["gold"]))
        attempt_tp += a_metrics["tp"]
        attempt_fp += a_metrics["false_positives"]
        attempt_fn += a_metrics["false_negatives"]
        unmatched_gold = list(record["gold"])
        for p, good in zip(record["predictions"], correctness):
            # Confusion alignment is stricter than utterance alone: construction is also fixed.
            anchor = next((g for g in unmatched_gold if g.get("learner_start") == p.get("learner_start") and normalized(g["learner_utterance"]) == normalized(p["learner_utterance"]) and g["construction"] == p["construction"]), None)
            confusion[(anchor["outcome"] if anchor else "extra", p["outcome"])] += 1
            if anchor:
                family_accuracy[p["construction"]]["aligned"] += 1
                family_accuracy[p["construction"]]["correct_outcome"] += p["outcome"] == anchor["outcome"]
                unmatched_gold.remove(anchor)
            if not good:
                failures.append({"session_id": record["session_id"], "kind": "unmatched_prediction", "prediction": p})
        for g in unmatched_gold:
            confusion[(g["outcome"], "missed")] += 1
            failures.append({"session_id": record["session_id"], "kind": "missing_observation", "gold": g})
        for block in record["blocks"]:
            ps = [p for p in record["predictions"] if block["source_start"] <= p["learner_start"] < block["source_end"]]
            gs = [g for g in record["gold"] if g["source_span"] == block["source_span"]]
            category_record = {"predictions": ps, "gold": gs}
            categories[block["category"]].append(category_record)
            if block["negative_error_control"]:
                negative_blocks += 1
                negative_errors += any(p["outcome"] == "incorrect" for p in ps)
    return {**ratios(tp, fp, fn), "predictions": predictions, "gold_observations": gold_count,
            "case_counts": {status: sum(r.get("status", "completed") == status for r in records) for status in ("completed", "invalid", "pending")},
            "schema_validation_failed_cases": sum(r.get("status") == "invalid" for r in records),
            "invalid_response_count": sum(i.get("status") == "invalid" for r in records for i in r.get("interactions", [])),
            "scored_sessions": sum(r.get("status") != "pending" for r in records),
            "total_sessions": len(records),
            "grammar_attempt_metrics": ratios(attempt_tp, attempt_fp, attempt_fn),
            "accepted_hallucinated_provenance": hallucinated, "rejected_provenance": rejected_provenance,
            "uncertain_observations": uncertainty, "abstention_rate": uncertainty / predictions if predictions else None,
            "sessions_with_no_predictions": sum(not r["predictions"] and r.get("status") != "pending" for r in records),
            "negative_error_control_blocks": negative_blocks, "negative_blocks_with_false_error": negative_errors,
            "negative_error_false_positive_rate": negative_errors / negative_blocks if negative_blocks else None,
            "by_construction": group_metrics([r for r in records if r.get("status") != "pending"], "construction"),
            "outcome_accuracy_by_construction": {family: {**counts, "accuracy_on_aligned": counts["correct_outcome"] / counts["aligned"] if counts["aligned"] else None} for family, counts in sorted(family_accuracy.items())},
            "by_evidence_type": group_metrics([r for r in records if r.get("status") != "pending"], "evidence_type"),
            "by_category": {c: combine_metrics(rs) for c, rs in sorted(categories.items())},
            "outcome_confusion_matrix": {f"{g}->{p}": n for (g, p), n in sorted(confusion.items())},
            "failures": failures}


def combine_metrics(records: list[dict]) -> dict:
    ms = [score_session(r["predictions"], r["gold"])[0] for r in records]
    return ratios(sum(m["tp"] for m in ms), sum(m["false_positives"] for m in ms), sum(m["false_negatives"] for m in ms))


def wilson(correct: int, count: int) -> list[float] | None:
    if not count:
        return None
    z = 1.959963984540054
    p = correct / count
    center = (p + z * z / (2 * count)) / (1 + z * z / count)
    half = z * ((p * (1 - p) / count + z * z / (4 * count * count)) ** .5) / (1 + z * z / count)
    return [max(0., center - half), min(1., center + half)]


def calibrate(records: list[dict], pipeline: dict, dataset: dict) -> dict:
    # Only calibration split may fit these buckets. No invented continuous confidence.
    if any(r["split"] != "calibration" for r in records):
        raise ValueError("Calibration fit requires calibration split exclusively")
    buckets = {}
    for score in range(1, 5):
        values = [good for r in records for p, good in zip(r["predictions"], r["correctness"]) if p["raw_support_score"] == score]
        n, k = len(values), sum(values)
        buckets[str(score)] = {"observations": n, "correct": k, "empirical_precision": k / n if n else None,
                               "wilson_interval_95": wilson(k, n), "support_tier": "unmeasured" if not n else "observed-high" if k / n >= .95 else "observed-medium" if k / n >= .8 else "observed-low"}
    return {"version": "support-calibration-1", "created_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": pipeline, "dataset": dataset, "split": "calibration",
            "method": "Exact-match accepted observation precision per deterministic support score; Wilson 95% descriptive intervals. No continuous probabilities exposed to learner state.",
            "limitations": "Synthetic templates and correlated observations make Wilson intervals optimistic; no real-world or cross-provider transfer is established.",
            "buckets": buckets}


def validate_calibration(calibration: dict, pipeline: dict, dataset: dict | None = None):
    if calibration["pipeline"]["pipeline_id"] != pipeline["pipeline_id"]:
        raise ValueError("Calibration pipeline mismatch; recalibrate, never silently reuse")
    if dataset is not None and calibration["dataset"] != dataset:
        raise ValueError("Calibration dataset mismatch")


def reliability(records: list[dict], calibration: dict) -> dict:
    buckets = {}
    for score in range(1, 5):
        values = [good for r in records for p, good in zip(r["predictions"], r["correctness"]) if p["raw_support_score"] == score]
        buckets[str(score)] = {"observations": len(values), "correct": sum(values),
                               "calibration_precision": calibration["buckets"][str(score)]["empirical_precision"],
                               "actual_precision": sum(values) / len(values) if values else None,
                               "wilson_interval_95": wilson(sum(values), len(values))}
    return {"buckets": buckets, "brier_score": None, "expected_calibration_error": None,
            "reason": "Support scores are tiers, not calibrated individual probabilities; Brier and ECE deliberately not asserted."}
