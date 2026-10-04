"""Controlled gold-IR evaluation of persistence, state, packs and lesson decisions.

This deliberately bypasses extraction/verifier. It cannot qualify an LLM runtime
or measure a student's learning gain. Expectations are authored in profiles.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

from thoth.artifacts import export_learner, write_json
from thoth.contracts import Observation, PipelineResult, digest
from thoth.engine import aggregate, lesson_targets
from thoth.storage import Store

FIXTURES = {
    "present_perfect.duration": ("I've lived here since 2021.", "I live here since 2021."),
    "present_perfect.vs_simple_past": ("I visited London yesterday.", "I've visited London yesterday."),
    "present_perfect.continuous": ("I've been studying all morning.", "I've studying all morning."),
    "duration.since_for": ("I've worked here for three years.", "I've worked here since three years."),
    "question.do_support": ("Where do you work?", "Where you work?"),
    "modal_perfect.should_have": ("I should have called her.", "I should called her."),
    "article.indefinite": ("I bought an umbrella.", "I bought a umbrella."),
    "auxiliary.chain": ("She has been working all morning.", "She has working all morning."),
}
SCOPES = ["contracts.py", "engine.py", "artifacts.py", "storage.py", "provenance.py", "profile_benchmark.py"]
GATES = {"all_preregistered_checks_pass": True, "unsafe_primary_decisions": 0,
         "invalid_evidence_citations": 0,
         "scope": "Synthetic downstream decision validation only; no LLM qualification or learning-gain claim"}


def metadata(dataset: Path) -> dict:
    root = Path(__file__).parent
    return {"dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
            "implementation": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SCOPES},
            "gates": GATES}


def materialize(profile: dict) -> list[dict]:
    """Build explicit report sources and annotated IR, without consulting engine."""
    result = []
    for number, session in enumerate(profile["sessions"]):
        raw = f"# Synthetic profile {profile['id']}, session {number + 1}\n\n"
        annotations = []
        for spec in session["runs"]:
            good, bad = FIXTURES[spec["family"]]
            if spec["family"] == "modal_perfect.should_have" and spec["feature"] == "question":
                good, bad = "Should I have called her?", "Should I called her?"
            if spec["family"] == "article.indefinite" and spec["feature"] == "negative":
                good, bad = "I didn't buy an umbrella.", "I didn't buy a umbrella."
            for event in spec["outcomes"]:
                block = len(annotations) + 1
                utterance = bad if event == "F" else good
                correction = good if event == "F" else None
                evidence = "explicit_correction" if event == "F" else "successful_use"
                outcome = "incorrect" if event == "F" else "correct"
                issue, decision = "grammar" if event == "F" else "none", "supported"
                note = (f'The teacher corrected this to: "{good}" The situation still continues.'
                        if event == "F" else "The sentence was correct in the reported context.")
                if event in "ORUT":
                    outcome = "uncertain"
                    if event == "O":
                        utterance, evidence = "That happened earlier.", "opportunity"
                        note = f"This was an opportunity for {spec['family']}; target was not selected."
                    elif event == "R":
                        utterance, evidence = f"{bad} Sorry, {good}", "self_correction"
                        note = "The learner repaired the sentence without a teacher prompt."
                    elif event == "U":
                        evidence, issue, decision = "other", "unclear", "uncertain"
                        note = "Context is missing; grammatical interpretation remains unresolved."
                    else:
                        evidence, issue = "other", "style"
                        note = "The teacher suggested a more formal style; this was not a grammatical error."
                span = (f"Block {block}. During {spec['mode']} conversation, the learner said: "
                        f'"{utterance}" {note}')
                start = len(raw)
                raw += span + "\n\n"
                learner_start = start + span.index(utterance)
                signals = dict(provenance=True, canonical=True, verifier=decision == "supported",
                               explicit_correction=event == "F")
                annotations.append(dict(id="OBS-" + digest([profile["id"], number, block])[:20],
                                        source_span=span, learner_utterance=utterance, corrected_form=correction,
                                        teacher_comment=None, construction=spec["family"], feature=spec["feature"],
                                        outcome=outcome, production_mode=spec["mode"], evidence_type=evidence,
                                        issue_kind=issue, source_start=start, source_end=start + len(span),
                                        learner_start=learner_start, learner_end=learner_start + len(utterance),
                                        pipeline_id="gold-ir-profiles-1", verifier_decision=decision,
                                        verifier_reason="Author-defined gold fixture; no model verdict executed.",
                                        support_signals=signals, raw_support_score=sum(signals.values())))
        sid = "SES-" + digest(raw)[:20]
        result.append(dict(id=sid, raw=raw,
                           occurred_on=str(date(2026, 1, 1) + timedelta(days=session["day"])),
                           observations=[Observation(session_id=sid, **o) for o in annotations]))
    return result


def evaluate_profile(profile: dict, output: Path) -> dict:
    fixtures = materialize(profile)
    output.mkdir(parents=True)
    with Store(output / "profile.db") as store:
        for session in fixtures:
            sid = store.save_session(session["raw"], profile["id"], session["occurred_on"])
            store.save_run(sid, PipelineResult(observations=session["observations"], rejected=[], trace=[],
                                               pipeline={"pipeline_id": "gold-ir-profiles-1", "provider": "gold-ir"}))
        observations, sessions = store.active()
        state = export_learner(output, observations, sessions)
        checks = []

        def check(name, expected, actual, category):
            checks.append(dict(name=name, category=category, expected=expected, actual=actual, passed=expected == actual))

        expected = profile["expected"]
        selected = lesson_targets(state)
        check("primary targets and rank", expected["primary"], selected["primary"], "primary")
        check("observed strengths", sorted(expected["strengths"]), selected["strengths"], "strength")
        for family in expected["collect"]:
            check(f"collect {family}", True, family in selected["observation"], "collection")
        check("construction coverage", sorted(expected["families"]), sorted(state["constructions"]), "facts")
        for family, gold in expected["families"].items():
            entry = state["constructions"].get(family, {})
            for mode, counts in gold["counts"].items():
                stats = entry.get("modes", {}).get(mode, {})
                check(f"{family}/{mode} successes, failures", counts,
                      [stats.get("successes"), stats.get("failures")], "facts")
                expected_mean = (counts[0] + 1) / (sum(counts) + 2)
                check(f"{family}/{mode} Beta mean", True,
                      math.isclose(expected_mean, stats.get("posterior_mean", -1), abs_tol=1e-12), "facts")
            for key in ("opportunities", "self_corrections", "uncertain_observations"):
                if key in gold:
                    check(f"{family}/{key}", gold[key], entry.get(key), "exclusions")
            if "trend" in gold:
                check(f"{family}/trend", gold["trend"], entry.get("trend", {}).get("label"), "trend")
            if gold.get("historical_only"):
                check(f"{family}/historical errors distinguished", True,
                      "Historical errors" in entry.get("interpretation", ""), "interpretation")
            if gold.get("mode_gap"):
                check(f"{family}/prompted or controlled gap described", True,
                      entry.get("mode_gap", {}).get("observed", False), "interpretation")
            for form in gold.get("missing_forms", []):
                check(f"{family}/{form} spontaneous coverage remains unknown", True,
                      any(form in text and "spontaneous" in text for text in entry.get("unknowns", [])), "coverage")
            pack = (output / "learner" / "evidence" / (family + ".md")).read_text()
            family_obs = [o for o in observations if o.construction == family]
            check(f"{family}/all provenance and IDs rendered", True,
                  all(o.id in pack and o.learner_utterance in pack
                      and f"[{o.source_start}, {o.source_end})" in pack for o in family_obs), "provenance")
        brief = (output / "learner" / "next-lesson.md").read_text()
        primary_lines = brief.split("## Primary practice targets\n", 1)[1].split("## Observation targets", 1)[0]
        for family in selected["primary"]:
            failures = [o for o in observations if o.construction == family and o.production_mode.value == "spontaneous"
                        and o.outcome.value == "incorrect" and o.evidence_type.value in {"explicit_correction", "inferred_error"}
                        and o.verifier_decision == "supported" and o.issue_kind == "grammar"]
            line = next((s for s in primary_lines.splitlines() if f"`{family}`" in s), "")
            cited_dates = {sessions[o.session_id]["occurred_on"] for o in failures if o.id in line}
            check(f"{family}/practice justified by failed quotes on distinct dates", True,
                  len(cited_dates) >= 2, "citations")
        check("order invariance", state, aggregate(list(reversed(observations)), dict(reversed(list(sessions.items())))), "invariance")
        # Re-ingestion/reprocessing replaces the active run, never duplicates attempts.
        first = fixtures[0]
        sid = store.save_session(first["raw"], profile["id"], first["occurred_on"])
        store.save_run(sid, PipelineResult(observations=first["observations"], rejected=[], trace=[],
                                         pipeline={"pipeline_id": "gold-ir-profiles-1"}))
        check("reprocessing invariance", state, aggregate(*store.active()), "invariance")
    serialized = [{**s, "observations": [o.model_dump(mode="json") for o in s["observations"]]} for s in fixtures]
    write_json(output / "gold-input.json", serialized)
    # Large state equality checks only need a boolean in the audit, not duplicate full packs.
    for item in checks:
        if item["category"] == "invariance":
            item["expected"], item["actual"] = True, item["passed"]
    result = dict(id=profile["id"], description=profile["description"], expected=expected,
                  selected=selected, sessions=len(fixtures), observations=len(observations),
                  passed=all(c["passed"] for c in checks), checks=checks)
    write_json(output / "result.json", result)
    return result


def run(dataset: Path, split: str, output: Path, freeze: Path | None = None) -> dict:
    before = metadata(dataset)
    if split == "holdout":
        if freeze is None or json.loads(freeze.read_bytes()) != before:
            raise ValueError("Freeze the implementation, expectations and gates before evaluating holdout")
    if output.exists():
        raise ValueError("Use a new output directory; previous profile evaluations are preserved")
    profiles = [p for p in json.loads(dataset.read_bytes())["profiles"] if p["split"] == split]
    if not profiles or len({p["id"] for p in profiles}) != len(profiles):
        raise ValueError("Empty split or duplicate profile IDs")
    results = [evaluate_profile(p, output / "profiles" / p["id"]) for p in profiles]
    checks = [c for r in results for c in r["checks"]]
    tp = sum(len(set(r["expected"]["primary"]) & set(r["selected"]["primary"])) for r in results)
    fp = sum(len(set(r["selected"]["primary"]) - set(r["expected"]["primary"])) for r in results)
    fn = sum(len(set(r["expected"]["primary"]) - set(r["selected"]["primary"])) for r in results)
    categories = {category: dict(total=sum(c["category"] == category for c in checks),
                                passed=sum(c["category"] == category and c["passed"] for c in checks))
                  for category in sorted({c["category"] for c in checks})}
    report = dict(metadata=before, split=split, scope=GATES["scope"],
                  profiles=len(results), profiles_passed=sum(r["passed"] for r in results),
                  sessions=sum(r["sessions"] for r in results), observations=sum(r["observations"] for r in results),
                  checks=len(checks), checks_passed=sum(c["passed"] for c in checks), categories=categories,
                  primary=dict(true_positives=tp, false_positives=fp, false_negatives=fn,
                               precision=tp / (tp + fp) if tp + fp else None,
                               recall=tp / (tp + fn) if tp + fn else None),
                  decision_suite_passed=all(r["passed"] for r in results),
                  real_student_readiness="NOT_ESTABLISHED", learning_gain="NOT_MEASURED",
                  limitations=["Gold IR bypasses the LLM extractor and verifier.",
                               "Dataset and expectations share an author; holdout is reserved execution, not independent blinded review.",
                               "Synthetic outcomes do not measure generalization, retention or causal learning gain."],
                  results=results)
    if metadata(dataset) != before:
        raise ValueError("Inputs or implementation changed during evaluation")
    write_json(output / "report.json", report)
    lines = ["# Validação de decisões por perfil", "", f"Split: {split}; {report['profiles_passed']}/{len(results)} perfis aprovados; "
             f"{report['checks_passed']}/{len(checks)} verificações aprovadas.", "",
             "Escopo: gold IR → persistência → learner state → Evidence Packs → lesson brief.",
             "Extração LLM não executada. Ganho de aprendizado não medido. Prontidão real: NOT_ESTABLISHED.", "",
             "| Perfil | Resultado | Conclusão esperada |", "|---|---|---|", ]
    lines += [f"| [{r['id']}](profiles/{r['id']}/learner/next-lesson.md) | {'PASS' if r['passed'] else 'FAIL'} | {r['description']} |" for r in results]
    lines += ["", "## Falhas", ""]
    lines += [f"- {r['id']}: {c['name']}; esperado `{c['expected']}`, obtido `{c['actual']}`."
              for r in results for c in r["checks"] if not c["passed"]] or ["Nenhuma falha nos critérios pré-definidos."]
    lines += ["", "## Limites", "", *["- " + s for s in report["limitations"]], ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["freeze", "development", "holdout"])
    parser.add_argument("--dataset", type=Path, default=Path("benchmark/profiles.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/profiles/development"))
    parser.add_argument("--freeze-file", type=Path, default=Path("reports/profiles/freeze.json"))
    args = parser.parse_args(argv)
    if args.action == "freeze":
        if args.freeze_file.exists():
            raise ValueError("Refusing to replace an existing profile freeze")
        write_json(args.freeze_file, metadata(args.dataset))
        print(f"Frozen: {args.freeze_file}")
        return 0
    report = run(args.dataset, args.action, args.output, args.freeze_file)
    print(json.dumps({k: report[k] for k in ("profiles", "profiles_passed", "checks", "checks_passed", "primary",
                                            "decision_suite_passed", "real_student_readiness", "learning_gain")}, indent=2))
    return 0 if report["decision_suite_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
