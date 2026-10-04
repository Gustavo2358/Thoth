from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from thoth.artifacts import export, write_json
from thoth.embeddings import LocalEmbedder
from thoth.llm import ManualChatGPTAdapter, OpenAIAdapter, PendingResponse
from thoth.pipeline import ingest, policy_from_file
from thoth.storage import Store


def main(argv=None):
    parser = argparse.ArgumentParser(prog="thoth", description="Discover patterns in English speaking evidence")
    parser.add_argument("--db", type=Path, default=Path("data/thoth.db"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    parser.add_argument("--policy", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("ingest")
    command.add_argument("file", type=Path)
    command.add_argument("--date", required=True)
    for name in ["state", "patterns", "next-lesson"]:
        sub.add_parser(name)
    command = sub.add_parser("import", help="Import original model responses named <request-hash>.txt")
    command.add_argument("directory", type=Path)
    command.add_argument("--exchange", type=Path, default=Path("data/exchange"))
    command.add_argument("--model", default="ChatGPT / unspecified")
    command = sub.add_parser("benchmark")
    command.add_argument("--split", choices=["development", "calibration", "holdout", "review", "calibrate", "freeze"], required=True)
    command.add_argument("--output", type=Path, default=Path("reports/benchmark"))
    command.add_argument("--freeze-file", type=Path, default=Path("benchmark/freeze.json"))
    for name in ["ingest", "benchmark"]:
        command = sub.choices[name]
        command.add_argument("--provider", choices=["manual", "openai"], default="manual")
        command.add_argument("--model", default="ChatGPT / unspecified")
        command.add_argument("--exchange", type=Path, default=Path("data/exchange"))
        command.add_argument("--interactive", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            print(ManualChatGPTAdapter(args.exchange, args.model).import_responses(args.directory))
            return 0
        if args.command == "benchmark":
            from thoth.benchmark import calibration, freeze_metadata, run, review_benchmark
            if args.split == "review":
                llm = ManualChatGPTAdapter(args.exchange, args.model, args.interactive) if args.provider == "manual" else OpenAIAdapter(args.model)
                print(json.dumps(review_benchmark(llm, args.output), indent=2))
                return 0
            embedder = LocalEmbedder()
            if args.split == "calibrate":
                report = calibration(embedder, args.output)
                print(json.dumps({k: report[k] for k in ("policy", "pedagogical_retrieval", "raw_quote_retrieval")}))
                return 0
            policy = policy_from_file(args.policy)
            if args.split == "freeze":
                if args.freeze_file.exists():
                    raise ValueError("Freeze already exists; do not replace a qualified experiment")
                llm = ManualChatGPTAdapter(args.exchange, args.model) if args.provider == "manual" else OpenAIAdapter(args.model)
                write_json(args.freeze_file, freeze_metadata(embedder, policy, llm.metadata()))
                print(str(args.freeze_file))
                return 0
            llm = ManualChatGPTAdapter(args.exchange, args.model, args.interactive) if args.provider == "manual" else OpenAIAdapter(args.model)
            report = run(args.split, embedder, llm, policy, args.output, args.freeze_file)
            print(json.dumps(report["metrics"], indent=2))
            return 0
        policy = policy_from_file(args.policy)
        with Store(args.db) as store:
            if args.command == "ingest":
                date.fromisoformat(args.date)
                raw = args.file.read_bytes().decode("utf-8")
                llm = ManualChatGPTAdapter(args.exchange, args.model, args.interactive) if args.provider == "manual" else OpenAIAdapter(args.model)
                print(json.dumps(ingest(raw, args.date, store, LocalEmbedder(), llm, policy)))
            state = export(args.artifacts, store, policy)
            if args.command == "patterns":
                print(json.dumps(state["patterns"], indent=2, ensure_ascii=False))
            elif args.command == "next-lesson":
                print((args.artifacts / "next-lesson.md").read_text())
            else:
                print((args.artifacts / "learner-state.md").read_text())
        return 0
    except PendingResponse as error:
        print("Pending: " + str(error), file=sys.stderr)
        return 2
    except (ValueError, OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
