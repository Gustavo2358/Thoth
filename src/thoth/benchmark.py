from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from thoth.adapters import Adapter
from thoth.artifacts import write_json
from thoth.contracts import digest
from thoth.evaluation import calibrate, evaluate, reliability, score_session, validate_calibration
from thoth.llm import InvalidLLMResponse, PendingLLMResponse
from thoth.pipeline import pipeline_metadata, process
from thoth.provenance import locate, validate


def dataset_metadata(root: Path) -> tuple[dict, dict]:
    path = root / "manifest.json"
    manifest = json.loads(path.read_text())
    return manifest, {"version": manifest["dataset_version"], "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def check_dataset(root: Path, manifest: dict, split: str):
    directory = root / "datasets" / split
    expected = manifest["splits"][split]["sha256"]
    actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()}
    if actual != expected:
        raise ValueError(f"Dataset content differs from versioned manifest: {split}")


def run_split(root: Path, split: str, adapter: Adapter, manifest: dict,
              audit_root: Path | None = None) -> tuple[list[dict], dict]:
    check_dataset(root, manifest, split)
    records = []
    for path in sorted((root / "datasets" / split).glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        gold = json.loads(path.with_suffix(".gold.json").read_text())
        for block in gold["blocks"]:
            block["source_start"], block["source_end"] = locate(raw, block["source_span"])
        for g in gold["observations"]:
            start, end = locate(raw, g["source_span"])
            quote = re.search(r"\s+".join(re.escape(t) for t in g["learner_utterance"].split()), raw[start:end])
            g["learner_start"] = start + quote.start()
        # Provider never sees gold. Only the text enters process().
        interaction_start = len(getattr(adapter, "interactions", []))
        status, error, result = "completed", None, None
        try:
            result = process(raw, gold["session_id"], adapter)
        except PendingLLMResponse as failure:
            status, error = "pending", str(failure)
        except InvalidLLMResponse as failure:
            status, error = "invalid", str(failure)
        interactions = getattr(adapter, "interactions", [])[interaction_start:]
        invalid = 0
        for o in result.observations if result else []:
            try:
                actual = validate(raw, o.source_span, o.learner_utterance, o.corrected_form, o.teacher_comment)
                invalid += actual != (o.source_start, o.source_end)
            except ValueError:
                invalid += 1
        proposals = result.trace[0]["response"]["observations"] if result else []
        before_verifier = []
        for p in proposals:
            try:
                start, end = validate(raw, p["source_span"], p["learner_utterance"], p.get("corrected_form"), p.get("teacher_comment"))
                quote = re.search(r"\s+".join(re.escape(t) for t in p["learner_utterance"].split()), raw[start:end])
                p = {**p, "learner_start": start + quote.start()}
                before_verifier.append(p)
            except ValueError:
                pass
        record = {"session_id": gold["session_id"], "split": split, "status": status, "error": error,
                        "predictions": [o.model_dump(mode="json") for o in result.observations] if result else [],
                        "gold": gold["observations"], "blocks": gold["blocks"],
                        "accepted_invalid_provenance": invalid,
                        "rejected_provenance": sum(r.reason.startswith("provenance:") for r in result.rejected) if result else 0,
                        "provenance_valid_proposals_before_verifier": before_verifier,
                        "rejected": [r.model_dump(mode="json") for r in result.rejected] if result else [],
                        "trace": result.trace if result else interactions, "interactions": interactions}
        records.append(record)
        if audit_root is not None:
            archive_case(audit_root / gold["session_id"], raw, record, adapter, manifest["dataset_version"])
    return records, evaluate(records)


def archive_case(directory: Path, raw: str, record: dict, adapter: Adapter, dataset_version: str):
    import shutil
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "raw.md").write_text(raw, encoding="utf-8")
    write_json(directory / "metadata.json", {"dataset_version": dataset_version, "split": record["split"],
               "session_id": record["session_id"], "pipeline": pipeline_metadata(adapter)})
    write_json(directory / "gold.json", record["gold"])
    write_json(directory / "parsed.json", record["predictions"])
    metrics = None if record["status"] == "pending" else score_session(record["predictions"], record["gold"])[0]
    write_json(directory / "result.json", {"status": record["status"], "error": record["error"], "metrics": metrics,
                                         "trace": record["trace"]})
    for number, interaction in enumerate(record["interactions"], 1):
        source = Path(interaction["case_directory"])
        target = directory / "interactions" / f"{number:03d}-{interaction['stage'].lower()}"
        target.mkdir(parents=True, exist_ok=True)
        for filename in ("request.txt", "request.json", "response.txt", "capture.json", "parsed.json", "validation.json"):
            if (source / filename).exists():
                shutil.copyfile(source / filename, target / filename)
        if interaction["stage"] == "Extraction":
            for filename in ("request.txt", "response.txt"):
                if (source / filename).exists():
                    shutil.copyfile(source / filename, directory / filename)


def ablation(records: list[dict]) -> dict:
    before = [{**r, "predictions": r["provenance_valid_proposals_before_verifier"]} for r in records if r.get("status") != "pending"]
    # Full evaluation includes support-score-independent metrics; accepted source
    # invariants remain deterministic in both stages.
    baseline = evaluate(before)
    after = evaluate(records)
    return {"provenance_only": {k: baseline[k] for k in ("precision", "recall", "false_positives", "negative_blocks_with_false_error")},
            "with_verifier": {k: after[k] for k in ("precision", "recall", "false_positives", "negative_blocks_with_false_error")},
            "interpretation": "Same-pipeline comparison on calibration data; agreement is an observable signal, not independent proof. A different verifier model is configurable."}


def freeze(root: Path, adapter: Adapter, path: Path):
    manifest, dataset = dataset_metadata(root)
    # Verify manifest/content integrity without evaluating or reporting holdout examples.
    for split in manifest["splits"]:
        check_dataset(root, manifest, split)
    record = {"frozen_at": datetime.now(timezone.utc).isoformat(), "pipeline": pipeline_metadata(adapter), "dataset": dataset,
              "qualification_rules": {"minimum_grammar_precision": .95, "maximum_negative_error_rate": .02,
                                      "maximum_accepted_hallucinated_provenance": 0,
                                      "minimum_ambiguous_uncertain_or_absent_rate": .90,
                                      "real_model_required": True, "maximum_schema_failed_cases": 0},
              "note": "Pipeline and dataset frozen before first holdout evaluation; qualification outputs are archived. Never tune this version against holdout errors."}
    if path.exists():
        existing = json.loads(path.read_text())
        if existing["pipeline"] != record["pipeline"] or existing["dataset"] != dataset:
            raise ValueError("Existing freeze differs; create a new version with a NEW holdout")
        return existing
    write_json(path, record)
    return record


def percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def report_markdown(report: dict) -> str:
    metrics = report["metrics"]
    lines = ["# Final benchmark qualification", "", f"Recommendation: **{report['recommendation']}**", "",
             f"Run: {report['run_id']}; created: {report['created_at']}",
              f"Provider: {report['pipeline']['provider']}; extractor: {report['pipeline']['model']}; verifier: {report['pipeline']['verifier_model']}",
             f"Mode: {report['pipeline'].get('mode', report['pipeline']['provider'])}",
             f"Pipeline: `{report['pipeline']['pipeline_id']}`; dataset: `{report['dataset']['version']}`", "",
             "This report measures a frozen pipeline on synthetic holdout sessions. Offline rule results do not qualify an LLM or arbitrary real reports.", "",
             "## Composition", ""]
    for split, composition in report["composition"].items():
        lines.append(f"- {split}: {composition['sessions']} sessions; {composition['narrative_blocks']} narrative blocks; {composition['gold_observations']} gold observations; {composition['negative_error_control_blocks']} negative error controls; {composition['adversarial_blocks']} adversarial blocks.")
    lines += ["", "## Holdout results", "", "| Metric | Result |", "|---|---:|",
              f"| Exact-match precision | {percent(metrics['precision'])} |",
              f"| Recall | {percent(metrics['recall'])} |", f"| F1 | {percent(metrics['f1'])} |",
              f"| False positive observations | {metrics['false_positives']} |",
              f"| False negatives | {metrics['false_negatives']} |",
              f"| Grammar-attempt precision | {percent(metrics['grammar_attempt_metrics']['precision'])} |",
              f"| Accepted hallucinated provenance | {metrics['accepted_hallucinated_provenance']} |",
              f"| Rejected invalid provenance proposals | {metrics['rejected_provenance']} |",
              f"| Cases with invalid original model JSON/schema | {metrics['schema_validation_failed_cases']} |",
              f"| Uncertain accepted observations | {metrics['uncertain_observations']} |",
              f"| Abstention rate (uncertain / accepted) | {percent(metrics['abstention_rate'])} |",
              f"| Negative control blocks with false grammar error | {metrics['negative_blocks_with_false_error']} / {metrics['negative_error_control_blocks']} |",
              f"| Ambiguous blocks with uncertainty or no grammar fact | {percent(report['ambiguity_safe_rate'])} |", "",
              "## By construction", "", "| Construction | TP | FP | FN | Precision | Recall | F1 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for family, m in metrics["by_construction"].items():
        lines.append(f"| {family} | {m['tp']} | {m['false_positives']} | {m['false_negatives']} | {percent(m['precision'])} | {percent(m['recall'])} | {percent(m['f1'])} |")
    lines += ["", "## By evidence type", "", "| Evidence | Precision | Recall | FP | FN |", "|---|---:|---:|---:|---:|"]
    for evidence, m in metrics["by_evidence_type"].items():
        lines.append(f"| {evidence} | {percent(m['precision'])} | {percent(m['recall'])} | {m['false_positives']} | {m['false_negatives']} |")
    lines += ["", "## Ambiguous and adversarial categories", "", "| Category | Precision | Recall | FP | FN |", "|---|---:|---:|---:|---:|"]
    for category, m in metrics["by_category"].items():
        lines.append(f"| {category} | {percent(m['precision'])} | {percent(m['recall'])} | {m['false_positives']} | {m['false_negatives']} |")
    lines += ["", "## Outcome confusion matrix", "", "Rows/columns use exact learner utterance + construction alignment; missed and extra are explicit.", ""]
    lines += [f"- {k}: {n}" for k, n in metrics["outcome_confusion_matrix"].items()]
    lines += ["", "## Support calibration", "", "Calibration is fitted only on calibration, never development or holdout. Scores are tiers, not individual probabilities.", "",
              "| Raw score | Calibration N | Calibration correct | Calibration precision | Wilson 95% interval | Holdout N | Holdout actual precision |",
              "|---|---:|---:|---:|---|---:|---:|"]
    for score, bucket in report["calibration"]["buckets"].items():
        held = report["reliability"]["buckets"][score]
        interval = bucket["wilson_interval_95"]
        display = "unmeasured" if interval is None else f"[{interval[0]:.3f}, {interval[1]:.3f}]"
        lines.append(f"| {score} | {bucket['observations']} | {bucket['correct']} | {percent(bucket['empirical_precision'])} | {display} | {held['observations']} | {percent(held['actual_precision'])} |")
    lines += ["", report["reliability"]["reason"], "", "### Verifier utility (calibration split)", "",
              "```json", json.dumps(report["verifier_ablation"], indent=2), "```", "",
              "## Matching and limitations", "", report["matching"], ""]
    lines += ["- " + limitation for limitation in report["limitations"]]
    lines += ["", "## Failures", "", f"Unmatched/missing observations: {len(metrics['failures'])}. The complete list is retained in benchmark-final.json. Below are examples; none were used to tune the frozen pipeline.", ""]
    for failure in metrics["failures"][:10]:
        obs = failure.get("prediction", failure.get("gold"))
        lines += [f"- {failure['session_id']} / {failure['kind']}: `{obs['construction']}` / {obs['outcome']} / {obs['evidence_type']}: “{obs['learner_utterance']}”"]
    lines += ["", "## Qualification", ""]
    lines += ["- " + reason for reason in report["qualification_reasons"]]
    lines += ["", "Manual ChatGPT is a real MVP runtime and can be qualified without API credentials. Record the selected model, preserve original responses, and use independent gold/new reserved cases. Calibration applies to this runtime and does not transfer automatically to an API model.", ""]
    return "\n".join(lines)


def qualify(root: Path, output: Path, adapter: Adapter, freeze_path: Path) -> dict:
    if not freeze_path.exists():
        raise ValueError("Freeze the pipeline before qualification")
    frozen = json.loads(freeze_path.read_text())
    manifest, dataset = dataset_metadata(root)
    pipeline = pipeline_metadata(adapter)
    if pipeline != frozen["pipeline"] or dataset != frozen["dataset"]:
        raise ValueError("Pipeline/dataset differs from frozen qualification version")
    run_id = "EVAL-" + uuid.uuid4().hex[:16]
    run_dir = output / "runs" / run_id
    run_dir.mkdir(parents=True)
    write_json(run_dir / "freeze.json", frozen)
    # Preserve completed calibration even if real-model holdout later fails.
    calibration_records, calibration_metrics = run_split(root, "calibration", adapter, manifest, run_dir / "cases" / "calibration")
    if calibration_metrics["case_counts"]["pending"]:
        progress = {"status": "pending", "run_id": run_id, "phase": "calibration", "metrics": calibration_metrics,
                    "message": "Original responses pending; no calibration or qualification published"}
        write_json(run_dir / "progress.json", progress)
        return progress
    calibration = calibrate(calibration_records, pipeline, dataset)
    write_json(run_dir / "calibration.json", calibration)
    write_json(run_dir / "calibration-predictions.json", calibration_records)
    validate_calibration(calibration, pipeline, dataset)
    holdout_records, metrics = run_split(root, "holdout_test", adapter, manifest, run_dir / "cases" / "holdout_test")
    if metrics["case_counts"]["pending"]:
        progress = {"status": "pending", "run_id": run_id, "phase": "holdout_test", "metrics": metrics,
                    "message": "Holdout responses pending; qualification not published"}
        write_json(run_dir / "progress.json", progress)
        return progress
    write_json(run_dir / "holdout-predictions.json", holdout_records)
    ambiguous = [(r, b) for r in holdout_records for b in r["blocks"] if b["category"] == "ambiguous"]
    safe = sum(not any(p["outcome"] != "uncertain" and b["source_start"] <= p["learner_start"] < b["source_end"] for p in r["predictions"]) for r, b in ambiguous)
    ambiguity_rate = safe / len(ambiguous) if ambiguous else None
    thresholds = frozen["qualification_rules"]
    reasons = []
    if pipeline["provider"] == "offline-rules":
        reasons.append("No actual LLM evaluation was executed: offline baseline quality is not evidence of real-model or real-report readiness.")
    elif pipeline["provider"] == "text-input":
        reasons.append("Chat-assisted text responses were evaluated, but the same assistant authored the synthetic experiment; independent blinded real-model validation remains unproven.")
    elif pipeline["provider"] == "manual-chatgpt" and pipeline.get("evaluation_design") != "independent":
        reasons.append("Manual ChatGPT is the intended runtime; independent evaluation design is unverified or shares authorship with gold. API access is not required.")
    if pipeline["provider"] == "manual-chatgpt" and pipeline["model"] == "ChatGPT / unspecified":
        reasons.append("Record the selected ChatGPT model label before qualification; the runtime is currently unspecified.")
    if metrics["schema_validation_failed_cases"] or calibration_metrics["schema_validation_failed_cases"]:
        reasons.append("Original model responses failed schema validation; failures are retained and scored, not repaired or omitted.")
    precision = metrics["grammar_attempt_metrics"]["precision"]
    if precision is None or precision < thresholds["minimum_grammar_precision"]:
        reasons.append("Grammar-attempt exact-match precision is below the preregistered 95% threshold.")
    if metrics["negative_error_false_positive_rate"] is None or metrics["negative_error_false_positive_rate"] > thresholds["maximum_negative_error_rate"]:
        reasons.append("Negative error control rate exceeds the preregistered 2% threshold or is unmeasured.")
    if metrics["accepted_hallucinated_provenance"]:
        reasons.append("Accepted source hallucination detected.")
    if ambiguity_rate is None or ambiguity_rate < thresholds["minimum_ambiguous_uncertain_or_absent_rate"]:
        reasons.append("Ambiguous safety rate is below the preregistered 90% threshold or is unmeasured.")
    report = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(), "pipeline": pipeline,
              "dataset": dataset, "composition": {s: {k: v for k, v in c.items() if k != "sha256"} for s, c in manifest["splits"].items()},
              "metrics": metrics, "calibration_metrics": calibration_metrics, "calibration": calibration,
              "reliability": reliability(holdout_records, calibration), "verifier_ablation": ablation(calibration_records),
              "ambiguity_safe_rate": ambiguity_rate, "frozen_at": frozen["frozen_at"],
              "recommendation": "NOT_READY_FOR_PERSONAL_PILOT" if reasons else "READY_FOR_PERSONAL_PILOT",
              "qualification_reasons": reasons or ["Frozen real-model pipeline passed the preregistered synthetic qualification gates; start only a supervised personal pilot."],
              "matching": "One-to-one multiset match within each session on exact learner character offset, whitespace-normalized utterance and correction, canonical construction, outcome, production mode, evidence type, issue kind, and feature. Predictions first undergo independent source-offset validation. No fuzzy matching. Identical quotes in different contexts cannot match each other. Per-construction precision/recall, not an inflated true-negative accuracy. Teacher-correction semantics must match too.",
              "limitations": ["Hand-authored gold and fixed narrative templates; lexical/time values and session documents are disjoint across splits, but grammatical templates overlap.",
                              "The holdout is untouched by execution until pipeline freeze, but is not an independently blinded human study.",
                              "Observations in a session are correlated. Bucket sample sizes are not independent students or real speaking sessions.",
                              "Exact provenance prevents nonexistent utterances, but source presence alone cannot prove semantic or speaker attribution accuracy.",
                              "Statistical learner accuracy is conditional on observed attempts; missing opportunities and selective teacher reporting cause sampling bias.",
                              "No generalization to ASR/transcripts, arbitrary report phrasing, real student speech, or different pipeline versions has been demonstrated."]}
    write_json(run_dir / "benchmark-final.json", report)
    (run_dir / "benchmark-final.md").write_text(report_markdown(report), encoding="utf-8")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("benchmark-final.json", "calibration.json", "benchmark-final.md"):
        (output / name).write_bytes((run_dir / name).read_bytes())
    return report
