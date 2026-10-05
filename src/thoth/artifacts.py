from __future__ import annotations

import json
import shutil
from pathlib import Path

from thoth.engine import learner_state
from thoth.compiler import compile_prompt
from thoth.teaching import teaching_state
from thoth.llm import immutable


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def evidence(records):
    lines = []
    for r in records:
        o = r["observation"]
        lines += [f"### {o.id}", "", f"Session: {o.session_id}; date: {r['occurred_on']}",
                  f"Mode: {o.production_mode}; performance: {o.performance}; evidence: {o.evidence_type}",
                  "", "> " + o.learner_quote, "", "Intent: " + o.communicative_intent,
                  "Production ability: " + o.learning_dimension, "Observed behavior: " + o.observed_behavior,
                  "Suggested alternatives (model suggestions, not reported corrections): " + (" / ".join(o.suggested_forms) or "none"),
                  "Hypothesis (not a mental-process fact): " + (o.hypothesis or "none"),
                  f"Review: {o.review.decision} — {o.review.reason}",
                  f"Grouping: {r['resolution'].decision} — {r['resolution'].reason}",
                  "Compared evidence: " + (r["resolution"].candidate_id or "none") + "; membership root: " + r["root_id"],
                  f"Conversation source [{o.source_start}, {o.source_end}); learner turn {o.turn}; lines {o.source_line_start}-{o.source_line_end}; support {o.support} from turns {o.support_turns}:", "",
                  *("> " + line for line in o.source_excerpt.splitlines()), ""]
    return "\n".join(lines)


def pattern_summary(pattern):
    lines = [f"## {pattern['label']} — {pattern['id']}", "",
             "Evidence-grounded model description (hypothesis): " + pattern["description"], "",
             f"Evidence: {pattern['observations']} observations, {pattern['sessions']} sessions, {pattern['dates']} distinct dates.",
             "", "| Mode | Successful | Difficulty | Uncertain |", "|---|---:|---:|---:|"]
    lines += [f"| {mode} | {c['successful']} | {c['difficulty']} | {c['uncertain']} |" for mode, c in pattern["modes"].items()]
    lines += ["", f"Opportunities: {pattern['opportunities']}; self-repairs: {pattern['self_corrections']}",
              f"Recent spontaneous: {pattern['recent_successes']} successful, {pattern['recent_difficulties']} difficulty.",
              f"Lesson status: {pattern['status']}", "Interpretation: " + pattern["interpretation"],
              "Mode comparison: " + pattern["mode_note"], "", "Unknowns:",
              *("- " + text for text in pattern["unknowns"]), "",
              "Evidence IDs: " + ", ".join(pattern["evidence_ids"]), ""]
    return "\n".join(lines)


def export(root, store, policy):
    root = Path(root)
    state = learner_state(store, policy)
    write_json(root / "learner-state.json", state)
    (root / "learner-state.md").write_text("# Current Learner State\n\n" +
          f"{state['sessions']} sessions; {state['observations']} observations; {len(state['patterns'])} patterns.\n\n" +
          "\n".join("- " + a for a in state["assumptions"]) + "\n\n" +
          "\n".join(pattern_summary(p) for p in state["patterns"]) +
          "\n## Isolated observations\n\n" + "\n".join(f"- {o['id']}: {o['dimension']}" for o in state["isolated"]) + "\n")
    prompt, audit = compile_prompt(store, policy)
    (root / "teacher-prompt.md").write_text(prompt, encoding="utf-8")
    write_json(root / "teacher-prompt.audit.json", audit)
    write_json(root / "teaching-model.json", teaching_state(store))
    write_json(root / "goals.json", store.goals())
    records = store.records()
    # Derived packs are current views, not a second historical product path.
    patterns_dir = root / "patterns"
    if patterns_dir.exists():
        shutil.rmtree(patterns_dir)
    patterns_dir.mkdir()
    for p in state["patterns"]:
        members = [r for r in records if r["root_id"] == p["root_id"]]
        (patterns_dir / (p["id"] + ".md")).write_text("# Pattern Evidence Pack\n\n" + pattern_summary(p) + "\n" + evidence(members))
    for session in store.sources():
        directory = root / "sessions" / session["id"]
        directory.mkdir(parents=True, exist_ok=True)
        immutable(directory / "conversation.md", session["raw"].encode("utf-8"))
        write_json(directory / "audit.json", json.loads(session["audit"]))
        (directory / "evidence-pack.md").write_text("# Session Evidence Pack\n\n" + evidence([r for r in records if r["session_id"] == session["id"]]))
    return state
