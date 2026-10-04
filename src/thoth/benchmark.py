from __future__ import annotations

import hashlib
import itertools
import json
import sqlite3
from collections import Counter
from pathlib import Path

import numpy as np

from thoth.artifacts import export, write_json
from thoth.contracts import Observation, Policy
from thoth.embeddings import pedagogical_text
from thoth.llm import PendingResponse
from thoth.pipeline import resolve
from thoth.storage import Store
from thoth.contracts import Review
from thoth import prompts


def dataset(split):
    path = Path("benchmark/data") / split
    sessions = json.loads((path / "sessions.json").read_bytes())
    gold = json.loads((path / "gold.json").read_bytes())
    return sessions, gold


def describe(values):
    return {"n": len(values), "min": float(min(values)), "median": float(np.median(values)),
            "max": float(max(values)), "p10": float(np.quantile(values, .1)), "p90": float(np.quantile(values, .9))} if values else {"n": 0}


def embedding_pair_ablation(split, embedder, cutoff):
    sessions, gold = dataset(split)
    observations = [Observation.model_validate(o) for s in sessions for o in s["observations"]]
    vectors = embedder.embed([pedagogical_text(o) for o in observations])
    tp = fp = fn = 0
    for i, j in itertools.combinations(range(len(observations)), 2):
        a, b = observations[i], observations[j]
        if a.review.decision != "keep" or b.review.decision != "keep":
            continue
        same = gold[a.id]["group"] is not None and gold[a.id]["group"] == gold[b.id]["group"]
        predicted = float(vectors[i] @ vectors[j]) >= cutoff
        tp += same and predicted
        fp += predicted and not same
        fn += same and not predicted
    return {"cutoff_from_calibration": cutoff, "true_same_pairs": tp, "false_merge_pairs": fp,
            "false_split_pairs": fn, "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "scope": "Independent pair classification research baseline, not transitive clustering or a runtime decision path"}


def calibration(embedder, output):
    sessions, gold = dataset("calibration")
    observations = [Observation.model_validate(o) for s in sessions for o in s["observations"]]
    vectors = embedder.embed([pedagogical_text(o) for o in observations])
    raw_vectors = embedder.embed([o.learner_quote for o in observations])

    def retrieval_curve(vs):
        totals, hits, history = 0, Counter(), []
        for o, vector in zip(observations, vs):
            group = gold[o.id]["group"]
            relevant = [r for r in history if group is not None and gold[r["id"]]["group"] == group]
            if relevant and o.review.decision == "keep":
                totals += 1
                ranked = sorted(history, key=lambda r: (-float(np.dot(vector, r["vector"])), r["id"]))
                for k in range(1, 7):
                    hits[k] += any(gold[r["id"]]["group"] == group for r in ranked[:k])
            if o.review.decision == "keep":
                history.append(dict(id=o.id, vector=vector))
        return {str(k): {"queries": totals, "hits": hits[k], "recall": hits[k] / totals if totals else None} for k in range(1, 7)}

    curve, raw_curve = retrieval_curve(vectors), retrieval_curve(raw_vectors)
    eligible = [k for k in range(1, 7) if curve[str(k)]["recall"] == 1]
    neighbors = min(eligible) if eligible else max(range(1, 7), key=lambda k: curve[str(k)]["recall"])
    same, different = [], []
    for i, j in itertools.combinations(range(len(observations)), 2):
        a, b = observations[i], observations[j]
        if a.review.decision != "keep" or b.review.decision != "keep":
            continue
        shared = gold[a.id]["group"] is not None and gold[a.id]["group"] == gold[b.id]["group"]
        (same if shared else different).append(float(np.dot(vectors[i], vectors[j])))
    # Promotion/priority outcomes are judged on every temporal prefix. Gold
    # recurring groups require independent dates; a two-date group stays collect.
    pattern_trials, practice_trials = [], []
    for threshold in [2, 3]:
        missed = premature = 0
        for group in {g["group"] for g in gold.values()} - {None}:
            dates = {s["occurred_on"] for s in sessions for o in s["observations"] if gold[o["id"]]["group"] == group}
            expected = len(dates) >= 2
            actual = len(dates) >= threshold
            missed += expected and not actual
            premature += not expected and actual
        pattern_trials.append(dict(dates=threshold, missed=missed, premature=premature))
    for threshold in [2, 3, 4]:
        wrong = 0
        for cutoff in [s["occurred_on"] for s in sessions]:
            for group in {g["group"] for g in gold.values()} - {None}:
                dates = {s["occurred_on"] for s in sessions if s["occurred_on"] <= cutoff
                         for o in s["observations"] if gold[o["id"]]["group"] == group}
                # The annotated pedagogy intentionally treats two dates as emerging,
                # not a practice diagnosis. This is a small conservative design study.
                expected = len(dates) >= 3
                wrong += expected != (len(dates) >= threshold)
        practice_trials.append(dict(dates=threshold, incorrect_prefix_decisions=wrong))
    pattern_dates = min(pattern_trials, key=lambda x: (x["premature"], x["missed"], x["dates"]))["dates"]
    practice_dates = min(practice_trials, key=lambda x: (x["incorrect_prefix_decisions"], x["dates"]))["dates"]
    policy = Policy(neighbors=neighbors, pattern_dates=pattern_dates, practice_dates=practice_dates)
    write_json(Path(__file__).with_name("policy.json"), policy.model_dump())
    # An embedding-only pair classifier can avoid all known false merges only by
    # setting a cutoff above the largest calibration different-pattern score.
    # Measure its missed same pairs; never install this cutoff in the runtime.
    baseline_cutoff = float(np.nextafter(max(different), float("inf")))
    report = {"embedding": embedder.metadata, "policy": policy.model_dump(), "pedagogical_retrieval": curve,
              "raw_quote_retrieval": raw_curve, "same_pair_similarities": describe(same),
              "different_pair_similarities": describe(different), "promotion_trials": pattern_trials,
              "practice_trials": practice_trials, "similarity_cutoff": None,
              "cutoff_reason": "Different-pattern similarities overlap same-pattern values; scores cannot decide membership. No cutoff removes candidates before semantic review.",
              "limitations": "Same-author reviewed IR; priority targets are a conservative pedagogical rubric, not an empirical learning-effect estimate.",
              "pair_distributions": {"same": same, "different": different},
              "embedding_only_pairs": embedding_pair_ablation("calibration", embedder, baseline_cutoff)}
    write_json(Path(output) / "calibration.json", report)
    return report


def freeze_metadata(embedder, policy, resolver=None):
    paths = sorted(Path(__file__).parent.glob("*.py")) + [Path(__file__).with_name("policy.json"), Path("requirements.lock"), Path("reports/calibration.json")]
    paths += sorted(Path("benchmark/data").glob("*/*.json"))
    return {"files": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            "embedding": embedder.metadata, "policy": policy.model_dump(), "resolver": resolver,
            "gates": {"false_merge_pairs": 0, "premature_patterns": 0, "missed_recurrences": 0,
                      "retrieval_recall_min": .95, "pairwise_recall_min": .90},
            "design": "Same-author synthetic reviewed IR + manual semantic adjudication; no independent blindness"}


def score(records, state, gold, retrieval):
    tp = false_merge = false_split = 0
    details = {"false_merge": [], "false_split": []}
    for a, b in itertools.combinations(records, 2):
        ga, gb = gold[a["id"]]["group"], gold[b["id"]]["group"]
        same_gold = ga is not None and ga == gb
        same_actual = a["root_id"] == b["root_id"]
        if same_gold and same_actual:
            tp += 1
        elif same_actual and not same_gold:
            false_merge += 1
            details["false_merge"].append([a["id"], b["id"]])
        elif same_gold and not same_actual:
            false_split += 1
            details["false_split"].append([a["id"], b["id"]])
    root_members = {}
    for r in records:
        root_members.setdefault(r["root_id"], []).append(r)
    recurring = {g for g in {v["group"] for v in gold.values()} - {None}
                 if len({r["occurred_on"] for r in records if gold[r["id"]]["group"] == g}) >= 2}
    covered = set()
    premature = []
    for p in state["patterns"]:
        members = root_members[p["root_id"]]
        groups = {gold[r["id"]]["group"] for r in members}
        if len(groups) == 1 and None not in groups and next(iter(groups)) in recurring:
            covered |= groups
        else:
            premature.append(p["id"])
    categories = Counter(r["actual"] for r in retrieval)
    resolution_scored = [r for r in retrieval if r["expected"] is not None]
    relevant = [r for r in retrieval if r["same_existed"]]
    conditional = [r for r in resolution_scored if not r["same_existed"] or r["retrieval_hit"]]
    precision = tp / (tp + false_merge) if tp + false_merge else None
    recall = tp / (tp + false_split) if tp + false_split else None
    return {"pairwise": {"true_same_pairs": tp, "false_merge_pairs": false_merge, "false_split_pairs": false_split,
                         "precision": precision, "recall": recall}, "pair_errors": details,
            "premature_patterns": premature, "missed_recurrences": sorted(recurring - covered),
            "retrieval": {"queries_with_prior_same": len(relevant), "hits": sum(r["retrieval_hit"] for r in relevant),
                          "recall": sum(r["retrieval_hit"] for r in relevant) / len(relevant) if relevant else None},
            "resolution": {"decisions": dict(categories), "queries": len(resolution_scored),
                           "correct": sum(r["actual"] == r["expected"] for r in resolution_scored),
                           "conditional_queries": len(conditional),
                           "conditional_correct": sum(r["actual"] == r["expected"] for r in conditional)},
            "notes": "Pairwise precision penalizes mixing abilities; recall penalizes separating manifestations of one ability. Singleton observations have no true pair and cannot improve recall by abstention."}


def run(split, embedder, llm, policy, output, freeze_file):
    output = Path(output)
    before = freeze_metadata(embedder, policy, llm.metadata() if llm is not None else None)
    if split == "holdout" and json.loads(Path(freeze_file).read_bytes()) != before:
        raise ValueError("Freeze current code, data, model and policy before opening holdout")
    if (output / "result.json").exists():
        raise ValueError("Evaluation exists; use a fresh output directory")
    sessions, gold = dataset(split)
    # Gold never goes into resolve(). It is used only below for scoring decisions.
    retrieval = []
    # Replay from a clean SQLite each time; original manual responses are cached.
    # A resumed experiment must not retrieve its own future/previously committed
    # sessions. Product ingestion uses the persistent Store, unchanged by this.
    with Store(":memory:") as store:
        for session in sessions:
            observations = [Observation.model_validate(o) for o in session["observations"]]
            vectors = embedder.embed([pedagogical_text(o) for o in observations])
            previous, records, summaries = store.records(), [], {}
            for o, vector in zip(observations, vectors):
                history = previous + records
                decision, root, retrieved = resolve(o, vector, history, store.patterns(), policy, llm)
                group, related = gold[o.id]["group"], gold[o.id]["related"]
                same_existed = group is not None and any(gold[r["id"]]["group"] == group for r in history)
                hit = any(any(gold[e["id"]]["group"] == group for e in c["evidence"]) for c in retrieved) if same_existed else False
                expected = "insufficient_evidence" if gold[o.id]["unresolved"] else "same_pattern" if same_existed else \
                           "related_but_different" if related and any(gold[r["id"]]["group"] == related for r in history) else "new_pattern"
                retrieval.append(dict(observation_id=o.id, expected=expected, actual=decision.decision,
                                      same_existed=same_existed, retrieval_hit=hit,
                                      candidates=[dict(candidate_id=c["candidate_id"], score=c["similarity"]) for c in retrieved]))
                if decision.decision == "same_pattern":
                    summaries[root] = (decision.pattern_label, decision.pattern_description, decision.conversation_contexts)
                records.append(dict(id=o.id, observation=o, root_id=root, vector=vector, occurred_on=session["occurred_on"],
                                    session_id=o.session_id, embedding_model=embedder.model, resolution=decision))
            store.commit_session(session["raw"], session["occurred_on"], records, summaries,
                                 {"model": llm.metadata(), "scope": "Reviewed synthetic IR → local embedding → actual semantic resolver",
                                  "interactions": llm.trace}, policy)
        state = export(output / "artifacts", store, policy)
        records = store.records()
        metrics = score(records, state, gold, retrieval)
        with sqlite3.connect(output / "learner.db") as saved:
            store.db.backup(saved)
    if freeze_metadata(embedder, policy, llm.metadata()) != before:
        raise ValueError("Implementation/data changed during the experiment")
    report = {"split": split, "metadata": before, "model": llm.metadata(), "metrics": metrics, "queries": retrieval,
              "sessions": len(sessions), "observations": len(records), "patterns": len(state["patterns"]),
              "learner_decisions": [{k: p[k] for k in ("id", "label", "status", "dates", "recent_successes", "recent_difficulties")} for p in state["patterns"]],
              "recommendation": "NOT_QUALIFIED_FOR_UNREVIEWED_USE", "learning_gain": "NOT_MEASURED"}
    gates = before["gates"]
    report["controlled_gates"] = {
        "no_false_merge": metrics["pairwise"]["false_merge_pairs"] == gates["false_merge_pairs"],
        "no_premature_pattern": len(metrics["premature_patterns"]) == gates["premature_patterns"],
        "no_missed_recurrence": len(metrics["missed_recurrences"]) == gates["missed_recurrences"],
        "retrieval": metrics["retrieval"]["recall"] is not None and metrics["retrieval"]["recall"] >= gates["retrieval_recall_min"],
        "pairwise_recall": metrics["pairwise"]["recall"] is not None and metrics["pairwise"]["recall"] >= gates["pairwise_recall_min"]}
    report["controlled_suite_passed"] = all(report["controlled_gates"].values())
    if split == "holdout":
        cutoff = json.loads(Path("reports/calibration.json").read_bytes())["embedding_only_pairs"]["cutoff_from_calibration"]
        report["embedding_only_pairs"] = embedding_pair_ablation(split, embedder, cutoff)
    write_json(output / "result.json", report)
    return report


def review_benchmark(llm, output):
    path = Path("benchmark/data/review")
    proposals = json.loads((path / "proposals.json").read_bytes())
    gold = json.loads((path / "gold.json").read_bytes())
    results, pending = [], []
    for p in proposals:
        o = p["observation"]
        try:
            review = llm.call("review", prompts.REVIEW, {"excerpt": o["source_excerpt"], "observation": o}, Review)
        except PendingResponse:
            pending.append(p["id"])
            continue
        results.append(dict(id=p["id"], expected=gold[p["id"]], actual=review.decision, reason=review.reason))
    if pending:
        raise PendingResponse(f"{len(pending)} review prompts exported in the exchange")
    kept = [r for r in results if r["actual"] == "keep"]
    expected_kept = [r for r in results if r["expected"] == "keep"]
    report = {"model": llm.metadata(), "cases": len(results), "correct": sum(r["expected"] == r["actual"] for r in results),
              "false_difficulties_before_review": sum(r["expected"] != "keep" for r in results),
              "false_difficulties_after_review": sum(r["expected"] != "keep" for r in kept),
              "valid_difficulties_lost": sum(r["actual"] != "keep" for r in expected_kept), "results": results,
              "design": "Same-author adversarial proposed observations; no independent model or annotation review"}
    write_json(Path(output) / "review-ablation.json", report)
    return report
