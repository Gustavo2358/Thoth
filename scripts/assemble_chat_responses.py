"""Formatting helper for THIS recorded chat experiment, not an LLM or extractor.

Only request transcripts and explicitly supplied operator decisions are read.
It mechanically substitutes exact quotes from repeated narrative templates. The
decisions were submitted in this chat after reading requests; they are NOT an
independent blind prediction, and must never qualify a provider API model.
"""
import argparse
import json
import re
from pathlib import Path

from thoth.artifacts import write_json
from thoth.contracts import Extraction, Verdict, digest

parser = argparse.ArgumentParser()
parser.add_argument("--exchange", type=Path, required=True)
parser.add_argument("--decisions", type=Path, required=True)
parser.add_argument("--split", required=True)
parser.add_argument("--stage", choices=("extraction", "verification"), required=True)
args = parser.parse_args()
decisions = json.loads(args.decisions.read_text())["items"]
submitted = 0
for path in sorted((args.exchange / "requests").glob("*.json")):
    req = json.loads(path.read_text())
    if args.stage == "extraction":
        if req["stage"] != "Extraction" or f"session {args.split}-" not in req["user_input"]["document"]:
            continue
        obs = []
        for block in req["user_input"]["document"].split("\n\n"):
            item = re.search(r"discussed item (\d+)\.", block)
            if not item:
                continue
            decisions_for_item = decisions[item.group(1)]
            if not decisions_for_item:
                continue
            learner = re.search(r'The learner said: "([^"]+)"', block).group(1)
            correction_match = re.search(r'corrected this to: "([^"]+)"', block)
            mode = "spontaneous" if block.startswith("During spontaneous") else "prompted" if block.startswith("During a prompted") else "controlled" if block.startswith("During a controlled") else "unknown"
            feature = "question" if learner.endswith("?") else "negative" if " not " in learner or "n't" in learner else "affirmative"
            for family, outcome, evidence, issue, _ in decisions_for_item:
                obs.append({"source_span": block.strip(), "learner_utterance": learner,
                            "corrected_form": correction_match.group(1) if correction_match and outcome == "incorrect" else None,
                            "teacher_comment": None, "construction": family, "outcome": outcome,
                            "production_mode": mode, "evidence_type": evidence, "feature": feature, "issue_kind": issue})
        response = Extraction.model_validate({"observations": obs}).model_dump(mode="json")
    else:
        if req["stage"] != "Verdict":
            continue
        p = req["user_input"]["proposal"]
        item = re.search(r"discussed item (\d+)\.", p["source_span"])
        if not item:
            continue
        # A distinct verifier pass was requested; linguistic verdicts are explicitly
        # supplied per case, not inferred from extractor/verifier agreement.
        # The same chat author still cannot supply independent blinded evidence.
        response = Verdict.model_validate(decisions[item.group(1)][p["construction"]]).model_dump(mode="json")
    envelope = {"request_sha256": req["request_sha256"], "submitted_by": "codex-chat/template-assisted",
                "decision_document_sha256": digest(decisions), "response": response,
                "limitations": "Same conversation authored synthetic cases and annotations. Repeated variants mechanically formatted. Not an independent blinded API evaluation."}
    destination = args.exchange / "responses" / path.name
    if destination.exists() and json.loads(destination.read_text()) != envelope:
        raise ValueError("Cannot overwrite a different recorded response")
    write_json(destination, envelope)
    submitted += 1
print(f"Submitted {submitted} {args.stage} response envelopes")
