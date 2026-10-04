"""Post-run diagnostics. Never supplies gold to a model or changes a prediction.

The original result.json and precommitted gates remain the primary result.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

from thoth.artifacts import write_json
from thoth.benchmark import dataset, describe
from thoth.contracts import Observation
from thoth.embeddings import LocalEmbedder, pedagogical_text


def analyze(split, directory):
    sessions, gold = dataset(split)
    report = json.loads((directory / "result.json").read_bytes())
    requests = {}
    audited = 0
    for path in (directory / "exchange").glob("*/request.json"):
        request = json.loads(path.read_bytes())
        response = (path.parent / "response.txt").read_bytes()
        assert hashlib.sha256(response).hexdigest() == (path.parent / "response.sha256").read_text()
        assert json.loads(response) == json.loads((path.parent / "parsed.json").read_bytes())
        audited += 1
        if request["stage"] == "resolve":
            data = json.loads(request["payload"]["messages"][1]["content"])
            requests[data["observation"]["id"]] = (data, json.loads(response))
    relations, conditional, memberships = [], [], []
    for q in report["queries"]:
        if q["observation_id"] not in requests:
            continue  # No history and unresolved review are system decisions.
        data, response = requests[q["observation_id"]]
        target = gold[q["observation_id"]]
        if q["expected"] == "related_but_different":
            available = any(gold[e["id"]]["group"] == target["related"]
                            for c in data["candidates"] for e in c["evidence"])
            relations.append(dict(id=q["observation_id"], candidate_available=available,
                                  expected=q["expected"], actual=q["actual"], quote=data["observation"]["learner_quote"]))
            if not available:
                continue
        if q["expected"] == "same_pattern" and not q["retrieval_hit"]:
            continue
        conditional.append(q["actual"] == q["expected"])
        if response["decision"] in {"same_pattern", "related_but_different"}:
            selected = next(c for c in data["candidates"] if c["candidate_id"] == response["candidate_id"])
            expected_group = target["group"] if response["decision"] == "same_pattern" else target["related"]
            memberships.append(any(gold[e["id"]]["group"] == expected_group for e in selected["evidence"]))
    observations = [Observation.model_validate(o) for s in sessions for o in s["observations"]]
    embedder = LocalEmbedder()
    pedagogical = embedder.embed([pedagogical_text(o) for o in observations])
    raw = embedder.embed([o.learner_quote for o in observations])
    retrieval = {}
    for label, vectors in [("pedagogical", pedagogical), ("raw_quote", raw)]:
        hits = {k: 0 for k in range(1, 7)}
        queries, previous = 0, []
        for i, o in enumerate(observations):
            group = gold[o.id]["group"]
            if group and any(gold[observations[j].id]["group"] == group for j in previous):
                queries += 1
                ranked = sorted(previous, key=lambda j: -float(vectors[i] @ vectors[j]))
                for k in hits:
                    hits[k] += any(gold[observations[j].id]["group"] == group for j in ranked[:k])
            if o.review.decision == "keep":
                previous.append(i)
        retrieval[label] = {k: dict(hits=v, queries=queries, recall=v / queries if queries else None) for k, v in hits.items()}
    same, different = [], []
    for i, j in itertools.combinations(range(len(observations)), 2):
        if observations[i].review.decision != "keep" or observations[j].review.decision != "keep":
            continue
        ga, gb = gold[observations[i].id]["group"], gold[observations[j].id]["group"]
        (same if ga and ga == gb else different).append(float(np.dot(pedagogical[i], pedagogical[j])))
    result = dict(scope="Post-holdout diagnostics; no policy or prediction edits. Conditional denominator excludes missing related targets as well as missing same targets.",
                  audited_original_responses=audited, actual_resolver_calls=len(requests),
                  related_retrieval=dict(queries=len(relations), hits=sum(r["candidate_available"] for r in relations), cases=relations),
                  resolution_given_available_candidates=dict(queries=len(conditional), correct=sum(conditional)),
                  selected_candidate_group=dict(queries=len(memberships), correct=sum(memberships)),
                  retrieval_ablation=retrieval, same_similarities=describe(same), different_similarities=describe(different))
    write_json(directory / "diagnostics.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("split", choices=["development", "calibration", "holdout"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.split, args.directory), indent=2))
