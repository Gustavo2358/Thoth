"""Run actual adapter extraction on reserved profile reports after qualification.

Unlike the gold-IR suite, observations here come only from process(raw, adapter).
No predictions are assembled from gold. Run after the frozen profile holdout.
"""
import argparse
import json
from pathlib import Path

from thoth.adapters import OfflineAdapter
from thoth.artifacts import export_learner, write_json
from thoth.engine import lesson_targets
from thoth.evaluation import evaluate
from thoth.llm import PendingLLMResponse
from thoth.manual_adapter import ManualChatGPTAdapter
from thoth.pipeline import pipeline_metadata, process
from thoth.profile_benchmark import materialize, metadata
from thoth.storage import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("benchmark/profiles.json"))
    parser.add_argument("--freeze-file", type=Path, default=Path("reports/profiles/freeze.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/profiles/offline-extraction"))
    parser.add_argument("--provider", choices=["offline", "manual"], default="offline")
    parser.add_argument("--profile", help="Optional single profile for a manual runtime smoke test")
    parser.add_argument("--exchange", type=Path)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--import", type=Path, dest="responses")
    parser.add_argument("--model", default="ChatGPT / unspecified")
    args = parser.parse_args()
    if json.loads(args.freeze_file.read_bytes()) != metadata(args.dataset):
        raise ValueError("Profile dataset and engine must match their freeze")
    if (args.output / "report.json").exists():
        raise ValueError("Use a new output directory")
    if args.provider == "manual":
        if args.exchange is None:
            raise ValueError("Manual evaluation needs --exchange")
        adapter = ManualChatGPTAdapter(args.exchange, args.model, export_directory=args.export,
                                       evaluation_design="same-author")
        if args.responses:
            print(json.dumps(adapter.import_responses(args.responses)))
    else:
        adapter = OfflineAdapter()
    records, decisions, pending = [], [], []
    for profile in json.loads(args.dataset.read_bytes())["profiles"]:
        if profile["split"] != "holdout":
            continue
        if args.profile and profile["id"] != args.profile:
            continue
        output = args.output / "profiles" / profile["id"]
        with Store(output / "profile.db") as store:
            for i, session in enumerate(materialize(profile)):
                sid = store.save_session(session["raw"], profile["id"], session["occurred_on"])
                try:
                    result = process(session["raw"], sid, adapter)
                except PendingLLMResponse as error:
                    pending.append(dict(session_id=sid, reason=str(error)))
                    continue
                store.save_run(sid, result)
                write_json(output / "sessions" / f"{i + 1}.json",
                           dict(raw=session["raw"], result=result.model_dump(mode="json")))
                gold = [o.model_dump(mode="json") for o in session["observations"]]
                records.append(dict(session_id=sid, predictions=[o.model_dump(mode="json") for o in result.observations],
                                    gold=gold, accepted_invalid_provenance=0,
                                    rejected_provenance=sum("provenance" in r.reason for r in result.rejected),
                                    blocks=[dict(source_start=g["source_start"], source_end=g["source_end"],
                                                 source_span=g["source_span"], category=g["construction"],
                                                 negative_error_control=g["outcome"] != "incorrect") for g in gold]))
            if pending:
                continue
            state = export_learner(output, *store.active())
            selected = lesson_targets(state)
            decisions.append(dict(id=profile["id"], expected_primary=profile["expected"]["primary"],
                                  actual_primary=selected["primary"],
                                  primary_correct=profile["expected"]["primary"] == selected["primary"],
                                  expected_strengths=profile["expected"]["strengths"], actual_strengths=selected["strengths"],
                                  strengths_correct=profile["expected"]["strengths"] == selected["strengths"]))
    if pending:
        write_json(args.output / "pending.json", dict(pending=pending, pipeline=pipeline_metadata(adapter)))
        print(json.dumps(dict(status="pending", sessions=len(pending))))
        return 2
    if not records:
        raise ValueError("No matching profile reports")
    metrics = evaluate(records)
    report = dict(profile_freeze=metadata(args.dataset), pipeline=pipeline_metadata(adapter),
                  scope="Actual adapter extraction → verifier → provenance → SQLite → packs",
                  metrics=metrics, decisions=decisions, recommendation="NOT_READY_FOR_REAL_STUDENT",
                  matching_scope="Author-defined local construction tags, not exhaustive incidental grammar. An unmatched extra correct construction is not automatically a linguistic error.",
                  evaluation_design="same-author synthetic; manual sample is an exposed smoke test, not independent qualification")
    write_json(args.output / "report.json", report)
    print(json.dumps(dict(precision=metrics["precision"], recall=metrics["recall"],
                          grammar=metrics["grammar_attempt_metrics"],
                          primary_correct=sum(d["primary_correct"] for d in decisions), profiles=len(decisions)), indent=2))
    (args.output / "pending.json").unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
