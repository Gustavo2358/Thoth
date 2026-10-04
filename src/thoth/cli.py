from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from thoth.adapters import adapter
from thoth.artifacts import export_learner, export_session, write_json
from thoth.benchmark import dataset_metadata, freeze, qualify, run_split
from thoth.pipeline import pipeline_metadata, process
from thoth.storage import Store
from thoth.llm import PendingLLMResponse
from thoth.contracts import digest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="learner", description="Speaking evidence with auditable sources and deterministic state")
    parser.add_argument("--db", type=Path, default=Path("data/app.db"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="Preserve source, extract, verify, persist, export")
    ingest.add_argument("file", type=Path)
    ingest.add_argument("--date", default=None, help="Session date YYYY-MM-DD (defaults to local date on first ingest)")
    reprocess = sub.add_parser("reprocess", help="Append a new extraction, preserving all old runs")
    reprocess.add_argument("session_id")
    for command in (ingest, reprocess):
        command.add_argument("--provider", "--llm", dest="provider", choices=("manual", "offline", "openai", "text"), default="manual",
                             help="Manual ChatGPT is the default subscription runtime; OpenAI is optional")
        command.add_argument("--model")
        command.add_argument("--verifier-model")
        command.add_argument("--responses-dir", type=Path)
        command.add_argument("--interactive", action="store_true", help="Paste JSON responses for the text adapter")
        command.add_argument("--export", type=Path, dest="export_directory", help="Export copyable prompts without gold")
        command.add_argument("--import", type=Path, dest="import_directory", help="Import original .txt model responses")
        command.add_argument("--evaluation-design", choices=("unverified", "same-author", "independent"), default="unverified")
    sub.add_parser("state", help="Rebuild JSON, Markdown and construction evidence packs")
    sub.add_parser("next-lesson", help="Rebuild lesson brief from active evidence")
    history = sub.add_parser("history")
    history.add_argument("session_id")
    requests = sub.add_parser("text-requests", help="Export schema prompts without exposing gold; rerun after extractor responses to export verifier prompts")
    requests.add_argument("--dataset", type=Path, default=Path("benchmark"))
    requests.add_argument("--split", choices=("development", "calibration", "holdout_test"), default="development")
    requests.add_argument("--responses-dir", type=Path, default=Path("benchmark/text-exchange"))
    requests.add_argument("--model", default="codex-session")
    requests.add_argument("--freeze-file", type=Path, default=Path("reports/pipeline-freeze.json"))
    for name in ("benchmark", "freeze"):
        command = sub.add_parser(name)
        command.add_argument("--provider", "--llm", dest="provider", choices=("manual", "offline", "openai", "text"), default="manual")
        command.add_argument("--model")
        command.add_argument("--verifier-model")
        command.add_argument("--responses-dir", type=Path)
        command.add_argument("--interactive", action="store_true")
        command.add_argument("--export", type=Path, dest="export_directory")
        command.add_argument("--import", type=Path, dest="import_directory")
        command.add_argument("--evaluation-design", choices=("unverified", "same-author", "independent"), default="unverified",
                             help="Recorded evaluation design declaration; independent is a declaration, not proof of blindness")
        command.add_argument("--dataset", type=Path, default=Path("benchmark"))
        command.add_argument("--freeze-file", type=Path, default=Path("reports/pipeline-freeze.json"))
        if name == "benchmark":
            command.add_argument("--split", choices=("development", "calibration", "holdout_test", "qualify"), default="development")
            command.add_argument("--output", type=Path, default=Path("reports/manual"))
    args = parser.parse_args(argv)
    try:
        if args.command == "text-requests":
            from thoth.text_adapter import TextAdapter
            from thoth.benchmark import check_dataset
            provider = TextAdapter(args.responses_dir, args.model)
            manifest, dataset = dataset_metadata(args.dataset)
            check_dataset(args.dataset, manifest, args.split)
            if args.split == "holdout_test":
                frozen = json.loads(args.freeze_file.read_text())
                if frozen["pipeline"] != pipeline_metadata(provider) or frozen["dataset"] != dataset:
                    raise ValueError("Freeze this pipeline/dataset before exporting holdout")
            pending = sum(provider.export_requests(p.read_bytes().decode("utf-8")) for p in sorted((args.dataset / "datasets" / args.split).glob("*.md")))
            print(f"Exported requests for {args.split}. Pending responses: {pending}. Directory: {args.responses_dir}")
            return 0
        if args.command in {"freeze", "benchmark"}:
            provider = configured_adapter(args)
            if args.command == "freeze":
                result = freeze(args.dataset, provider, args.freeze_file)
                print("Frozen pipeline: " + result["pipeline"]["pipeline_id"])
            elif args.split == "qualify":
                report = qualify(args.dataset, args.output, provider, args.freeze_file)
                if report.get("status") == "pending":
                    print(json.dumps(report, indent=2))
                    return 2
                print(json.dumps({"recommendation": report["recommendation"], "metrics": {k: report["metrics"][k] for k in ("precision", "recall", "f1", "false_positives", "accepted_hallucinated_provenance")}, "report": str(args.output / "benchmark-final.md")}, indent=2))
            else:
                manifest, dataset = dataset_metadata(args.dataset)
                pipeline = pipeline_metadata(provider)
                if args.split == "holdout_test":
                    frozen = json.loads(args.freeze_file.read_bytes())
                    if frozen["pipeline"] != pipeline or frozen["dataset"] != dataset:
                        raise ValueError("Freeze this pipeline/dataset before exporting or evaluating holdout")
                run_dir = args.output / "runs" / ("MANUAL-" + digest([pipeline, dataset, args.split])[:16])
                records, metrics = run_split(args.dataset, args.split, provider, manifest, run_dir / "cases")
                write_json(run_dir / "metadata.json", {"pipeline": pipeline, "dataset": dataset, "split": args.split})
                write_json(run_dir / "predictions.json", records)
                write_json(run_dir / "metrics.json", metrics)
                write_json(args.output / (args.split + "-predictions.json"), records)
                write_json(args.output / (args.split + "-metrics.json"), metrics)
                print(json.dumps({"run_directory": str(run_dir), **{k: metrics[k] for k in ("precision", "recall", "f1", "false_positives", "false_negatives", "accepted_hallucinated_provenance", "case_counts", "schema_validation_failed_cases", "invalid_response_count")}}, indent=2))
                if metrics["case_counts"]["pending"]:
                    return 2
                if metrics["schema_validation_failed_cases"]:
                    return 1
            return 0
        with Store(args.db) as store:
            if args.command == "history":
                print(json.dumps(store.history(args.session_id), indent=2))
                return 0
            if args.command in {"ingest", "reprocess"}:
                provider = configured_adapter(args)
                if args.command == "ingest":
                    raw = args.file.read_bytes().decode("utf-8")
                    # For idempotent re-ingestion retain the original date if omitted.
                    sid = "SES-" + digest(raw)[:20]
                    existing = store.db.execute("SELECT occurred_on FROM sessions WHERE id=?", (sid,)).fetchone()
                    occurred_on = args.date or (existing[0] if existing else date.today().isoformat())
                    sid = store.save_session(raw, args.file.name, occurred_on)
                else:
                    sid = args.session_id
                    raw = store.session(sid)["raw"]
                result = process(raw, sid, provider)
                run_id = store.save_run(sid, result)
                export_session(args.artifacts, store.session(sid), run_id, result)
                print(f"Session {sid}; run {run_id}; accepted {len(result.observations)}; rejected {len(result.rejected)}")
            observations, sessions = store.active()
            state = export_learner(args.artifacts, observations, sessions)
            if args.command == "next-lesson":
                print((args.artifacts / "learner" / "next-lesson.md").read_text())
            elif args.command == "state":
                print((args.artifacts / "learner" / "learner-state.md").read_text())
            else:
                print(f"Rebuilt state: {state['sessions']} sessions; {state['observations']} observations. Artifacts: {args.artifacts}")
        return 0
    except PendingLLMResponse as error:
        print(f"Pending: {error}", file=sys.stderr)
        return 2
    except (ValueError, OSError, RuntimeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def configured_adapter(args):
    if (args.export_directory is not None or args.import_directory is not None) and args.provider != "manual":
        raise ValueError("--export/--import are for --llm manual")
    provider = adapter(args.provider, args.model, args.verifier_model, args.responses_dir, args.interactive,
                       args.export_directory, args.evaluation_design)
    if args.import_directory is not None:
        print(json.dumps(provider.import_responses(args.import_directory)))
    return provider


if __name__ == "__main__":
    raise SystemExit(main())
