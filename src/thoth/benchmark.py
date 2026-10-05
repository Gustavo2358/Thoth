"""Evaluation helpers; never imported by product selection or extraction."""
import itertools
from collections import Counter


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
