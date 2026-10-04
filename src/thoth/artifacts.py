from __future__ import annotations

import json
from pathlib import Path

from thoth.contracts import Observation, PipelineResult, TAXONOMY
from thoth.engine import aggregate, lesson_targets


def write_json(path: Path, value: object):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def evidence_markdown(observations: list[Observation], title: str) -> str:
    lines = [f"# {title}", "", "Raw support scores are observable signals, not probabilities.", ""]
    for o in observations:
        lines += [f"## {o.id}", "", f"Session: {o.session_id}; construction: {o.construction}",
                  f"Outcome: {o.outcome.value}; mode: {o.production_mode.value}; evidence: {o.evidence_type.value}",
                  f"Verifier: {o.verifier_decision}; support score: {o.raw_support_score}/4; pipeline: {o.pipeline_id}",
                  f"Source offsets: [{o.source_start}, {o.source_end}) (Python Unicode characters)", "",
                  "Learner:", "", "> " + o.learner_utterance, ""]
        if o.corrected_form:
            lines += ["Reported correction (not automatically authoritative):", "", "> " + o.corrected_form, ""]
        lines += ["Verifier reason: " + o.verifier_reason, "", "Source excerpt:", "",
                  *("> " + line for line in o.source_span.splitlines()), ""]
    if not observations:
        lines += ["No accepted evidence; this is not a claim of error-free speech.", ""]
    return "\n".join(lines)


def export_session(root: Path, session: dict, run_id: str, result: PipelineResult):
    directory = root / "sessions" / session["id"]
    directory.mkdir(parents=True, exist_ok=True)
    raw_path = directory / "raw.md"
    if raw_path.exists() and raw_path.read_bytes().decode("utf-8") != session["raw"]:
        raise ValueError("Refusing to overwrite conflicting raw artifact")
    raw_path.write_text(session["raw"], encoding="utf-8")
    run_dir = directory / "runs" / run_id
    if run_dir.exists():
        raise ValueError("Refusing to overwrite an extraction artifact")
    run_dir.mkdir(parents=True)
    write_json(run_dir / "observations.json", [o.model_dump(mode="json") for o in result.observations])
    write_json(run_dir / "audit.json", result.model_dump(mode="json"))
    (run_dir / "evidence-pack.md").write_text(evidence_markdown(result.observations, "Session Evidence Pack"), encoding="utf-8")
    write_json(directory / "active-run.json", {"run_id": run_id, "pipeline_id": result.pipeline["pipeline_id"]})


def state_markdown(state: dict) -> str:
    lines = ["# Learner State", "", f"Sessions: {state['sessions']}; accepted observations: {state['observations']}", "",
             "Facts below are deterministic. Interpretations are hypotheses, not diagnoses.", ""]
    lines += ["- " + a for a in state["assumptions"]] + [""]
    for family, entry in state["constructions"].items():
        lines += [f"## {entry['label']} (`{family}`)", "", f"Sessions observed: {entry['sessions_observed']}; last seen: {entry['last_seen']}", "",
                  "| Production mode | Successes | Failures | Posterior mean | 95% credible interval |",
                  "|---|---:|---:|---:|---|"]
        for mode, stats in entry["modes"].items():
            lo, hi = stats["credible_interval_95"]
            estimate = f"{stats['posterior_mean']:.3f}" if stats["attempts"] else "prior only"
            lines.append(f"| {mode} | {stats['successes']} | {stats['failures']} | {estimate} | [{lo:.3f}, {hi:.3f}] |")
        lines += ["", "Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).",
                  f"Opportunities: {entry['opportunities']}; self-corrections: {entry['self_corrections']}; uncertain: {entry['uncertain_observations']}",
                  f"Trend: {entry['trend']['label']}", "", "Hypothesis: " + entry["interpretation"],
                  "Mode comparison: " + entry["mode_gap"]["interpretation"],
                  "Recent failed spontaneous evidence IDs: " + ", ".join(entry["practice_evidence_ids"]),
                  "", "Unknowns:", ""]
        lines += ["- " + x for x in entry["unknowns"]] or ["- Transfer to unobserved contexts remains untested."]
        lines += ["", "Recent evidence IDs: " + ", ".join(entry["recent_evidence_ids"]), ""]
    return "\n".join(lines)


def lesson_markdown(state: dict) -> str:
    selected = lesson_targets(state)
    lines = ["# Next Lesson Brief", "", "Focus on accurate spontaneous English production in natural conversation.", "",
             "## Primary practice targets", ""]
    lines += ["- " + TAXONOMY[f] + " (`" + f + "`): " + str(state["constructions"][f]["recent_spontaneous_failures"]) + " recent spontaneous failures; evidence: " + ", ".join(state["constructions"][f]["practice_evidence_ids"])
              for f in selected["primary"]] or ["- Insufficient repeated evidence for a primary difficulty. Collect evidence first."]
    lines += ["", "## Observation targets", ""]
    lines += ["- " + TAXONOMY[f] + ": collect spontaneous attempts, especially questions and negatives."
              for f in selected["observation"]] or ["- Broaden contexts and record both successful and unsuccessful attempts."]
    lines += ["", "## Observed strengths", ""]
    lines += ["- " + TAXONOMY[f] for f in selected["strengths"]] or ["- Insufficient data to claim a stable strength."]
    lines += ["", "## Teaching strategy", "",
              "- Favor spontaneous conversation; create natural contexts for targets without prescribing wording.",
              "- Do not interrupt every error. Record exact quotes and corrections after the conversation.",
              "- Test transfer to new topics; distinguish spontaneous speech from prompted and controlled practice.",
              "- Verify negative and question forms; avoid treating legitimate alternatives as failures.",
              "- Record non-selected targets as opportunities, separately from grammatical attempts.",
              "- Compare guided and spontaneous performance without diagnosing a retrieval cause.",
              "- Recheck dated evidence in today's conversation before choosing a practice task.",
              "", "## Selection rationale", "", selected["selection_rule"], ""]
    return "\n".join(lines)


def export_learner(root: Path, observations: list[Observation], sessions: dict) -> dict:
    state = aggregate(observations, sessions)
    learner = root / "learner"
    write_json(learner / "learner-state.json", state)
    (learner / "learner-state.md").write_text(state_markdown(state), encoding="utf-8")
    (learner / "next-lesson.md").write_text(lesson_markdown(state), encoding="utf-8")
    # Current derived packs are replaceable; immutable source/run artifacts are
    # elsewhere. Remove only our known generated construction outputs.
    for family in TAXONOMY.keys() - state["constructions"].keys():
        stale = learner / "evidence" / (family + ".md")
        if stale.exists() and stale.read_text(encoding="utf-8").startswith("# Learner State\n"):
            stale.unlink()
    for family, entry in state["constructions"].items():
        path = learner / "evidence" / (family + ".md")
        path.parent.mkdir(parents=True, exist_ok=True)
        pack = state_markdown({**state, "constructions": {family: entry}})
        pack += "\n" + evidence_markdown([o for o in observations if o.construction == family], "Auditable Evidence")
        path.write_text(pack, encoding="utf-8")
    return state
