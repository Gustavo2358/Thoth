"""Manually specified linguistic cases; no extractor, provider, or gold inference.

Templates only change lexical/time values and narrative wrappers. Labels are
authored here and do not consult the system under test. Do not tune holdout cases.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent
VERSION = "synthetic-1"

# (category, learner, correction, contextual note, gold labels)
# A label is (construction, outcome, evidence_type, issue_kind).
CASES = [
    ("positive", "I live here since {year}.", "I've lived here since {year}.", "The situation still continues.", [("present_perfect.duration", "incorrect", "explicit_correction", "grammar")]),
    ("successful", "I've worked here for {number} years.", None, "The situation still continues. The sentence was grammatically correct.", [("present_perfect.duration", "correct", "successful_use", "none")]),
    ("positive", "I have visited {city} yesterday.", "I visited {city} yesterday.", "The visit is a completed event.", [("present_perfect.vs_simple_past", "incorrect", "explicit_correction", "grammar")]),
    ("correct_control", "I visited {city} last year.", None, "The visit is a completed event. The sentence was grammatically correct.", [("present_perfect.vs_simple_past", "correct", "successful_use", "none")]),
    ("positive", "I have working on the project for {number} months.", "I have been working on the project for {number} months.", "The work still continues.", [("present_perfect.continuous", "incorrect", "explicit_correction", "grammar")]),
    ("successful", "I've been working on the project for {number} months.", None, "The work still continues. The sentence was grammatically correct.", [("present_perfect.continuous", "correct", "successful_use", "none")]),
    ("multiple", "I have lived here since {number} years.", "I have lived here for {number} years.", "The situation still continues. The tense is valid; the time preposition needs repair.", [("present_perfect.duration", "correct", "successful_use", "none"), ("duration.since_for", "incorrect", "explicit_correction", "grammar")]),
    ("multiple", "I've worked here for {year}.", "I've worked here since {year}.", "The situation still continues. The tense is valid; the time preposition needs repair.", [("present_perfect.duration", "correct", "successful_use", "none"), ("duration.since_for", "incorrect", "explicit_correction", "grammar")]),
    ("question", "Where you work?", "Where do you work?", "This is a direct neutral question, not an echo question.", [("question.do_support", "incorrect", "explicit_correction", "grammar")]),
    ("question", "Where does he work?", None, "This is a direct question. The sentence was grammatically correct.", [("question.do_support", "correct", "successful_use", "none")]),
    ("positive", "I should told my team about {topic}.", "I should have told my team about {topic}.", "The speaker regrets a past action.", [("modal_perfect.should_have", "incorrect", "explicit_correction", "grammar")]),
    ("negative_form", "I should not have sent the message about {topic}.", None, "The speaker regrets a past action. The sentence was grammatically correct.", [("modal_perfect.should_have", "correct", "successful_use", "none")]),
    ("positive", "She is a engineer in {city}.", "She is an engineer in {city}.", "We discussed her profession.", [("article.indefinite", "incorrect", "explicit_correction", "grammar")]),
    ("successful", "She is a developer in {city}.", None, "We discussed her profession. The sentence was grammatically correct.", [("article.indefinite", "correct", "successful_use", "none")]),
    ("negative_form", "I did not went to {city}.", "I did not go to {city}.", "The speaker described a cancelled trip.", [("auxiliary.chain", "incorrect", "explicit_correction", "grammar")]),
    ("successful", "I will be working on {topic}.", None, "The speaker described tomorrow's schedule. The sentence was grammatically correct.", [("auxiliary.chain", "correct", "successful_use", "none")]),
    ("style", "I think this implementation of {topic} is good.", "I think this is a solid implementation of {topic}.", "This is only a stylistic suggestion, a more natural phrasing. Original grammar is valid.", [("unclassified", "uncertain", "other", "style")]),
    ("ambiguous", "I worked there for {number} years.", None, "Insufficient context: we do not know if the employment ended.", [("present_perfect.duration", "uncertain", "other", "unclear")]),
    ("self_correction", "I work... sorry, I've worked here since {year}.", None, "The learner repaired the sentence without teacher help.", [("present_perfect.duration", "uncertain", "self_correction", "unclear")]),
    ("multiple", "I should told a information about {topic}.", "I should have told the information about {topic}.", "Two errors occurred: the modal form and the article on an uncountable noun.", [("modal_perfect.should_have", "incorrect", "explicit_correction", "grammar"), ("article.indefinite", "incorrect", "explicit_correction", "grammar")]),
    ("irrelevant", None, None, "We chatted about {topic} and shared plans for the weekend. Next meeting in {city}.", []),
    ("teacher_only", None, None, 'The teacher explained: "I should told my team about {topic}." The learner did not produce that sentence.', []),
    ("opportunity", "I started there {number} years ago.", None, 'The teacher asked: "How long have you worked there?" This was an opportunity; target was not selected. The answer was grammatically valid.', [("present_perfect.duration", "uncertain", "opportunity", "unclear")]),
    ("teacher_wrong", "I've lived here since {year}.", "I live here since {year}.", "The situation still continues. The teacher claimed that present tense was required, incorrectly.", [("present_perfect.duration", "correct", "successful_use", "none")]),
    ("ended_context", "I worked there for {number} years.", None, "This is an ended job: I no longer work there. The sentence was grammatically correct.", [("present_perfect.vs_simple_past", "correct", "successful_use", "none")]),
    ("paraphrase", "I started my job in {year}.", None, "The teacher wanted a duration construction, but this is a legitimate alternative. No correction was needed.", []),
    ("negative_form", "I have not lived here since {year}.", None, "The speaker moved away in that year. The sentence was grammatically correct.", [("present_perfect.duration", "correct", "successful_use", "none")]),
    ("question", "Why did you go?", None, "This is a direct question. The sentence was grammatically correct.", [("question.do_support", "correct", "successful_use", "none"), ("auxiliary.chain", "correct", "successful_use", "none")]),
    ("ambiguous", "I should tell my team about {topic}.", None, "Insufficient context: no evidence of a past unrealized action.", [("modal_perfect.should_have", "uncertain", "other", "unclear")]),
    ("teacher_wrong", "She is an engineer in {city}.", "She is a engineer in {city}.", "The teacher suggested a wrong article. The original was grammatical.", [("article.indefinite", "correct", "successful_use", "none")]),
    ("correct_control", "I like the music in {city}.", None, "This sentence is correct and outside the selected construction families.", []),
    ("vocabulary", "This algorithm for {topic} is fast.", "This algorithm for {topic} is efficient.", "A vocabulary suggestion, not a grammatical error. A more natural word was discussed.", [("unclassified", "uncertain", "other", "vocabulary")]),
]

NEGATIVES = {"style", "ambiguous", "opportunity", "self_correction", "teacher_wrong", "ended_context", "paraphrase", "correct_control", "irrelevant", "teacher_only", "vocabulary", "successful"}
ADVERSARIAL = {"style", "ambiguous", "opportunity", "self_correction", "teacher_wrong", "ended_context", "paraphrase", "teacher_only", "vocabulary", "multiple"}


def generate() -> dict:
    manifest = {"dataset_version": VERSION, "gold_source": "manually specified cases in build_dataset.py, never model output", "splits": {}}
    split_config = {
        "development": ([2020, 2021, 2022, 2023], ["two", "three", "four", "five"], ["London", "Dublin", "Paris", "Rome"], ["testing", "storage", "deployment", "metrics"]),
        "calibration": ([2016, 2017, 2018, 2019], ["six", "seven", "eight", "nine"], ["Madrid", "Oslo", "Boston", "Lima"], ["caching", "scheduling", "monitoring", "releases"]),
        "holdout_test": ([2012, 2013, 2014, 2015], ["ten", "eleven", "twelve", "thirteen"], ["Tokyo", "Sydney", "Berlin", "Lisbon"], ["routing", "backups", "migration", "indexing"]),
    }
    modes = ["spontaneous", "prompted", "controlled", "unknown"]
    for split, (years, numbers, cities, topics) in split_config.items():
        directory = ROOT / "datasets" / split
        directory.mkdir(parents=True, exist_ok=True)
        total_gold, negative_blocks, adversarial_blocks = 0, 0, 0
        outcome_counts = {"correct": 0, "incorrect": 0, "uncertain": 0}
        positive_error_blocks = 0
        checksums = {}
        # Eight sessions, sixteen narrative blocks each; combine cases to save API calls.
        for variant in range(4):
            values = dict(year=years[variant], number=numbers[variant], city=cities[variant], topic=topics[variant])
            for half in range(2):
                sid = f"{split}-{variant:02d}-{half}"
                blocks, gold, block_info = [], [], []
                for index in range(half * 16, (half + 1) * 16):
                    category, utterance, correction, note, labels = CASES[index]
                    mode = modes[(variant + index) % 4]
                    u = utterance.format(**values) if utterance else None
                    c = correction.format(**values) if correction else None
                    intro = {"spontaneous": "During spontaneous conversation", "prompted": "During a prompted speaking turn",
                             "controlled": "During a controlled drill", "unknown": "During the lesson"}[mode]
                    text = f"{intro} about {topics[variant]}, we discussed item {index + 1}. "
                    if u:
                        text += f'The learner said: "{u}" '
                    if c:
                        text += f'The teacher corrected this to: "{c}" '
                    text += note.format(**values)
                    blocks.append(text)
                    block_info.append({"index": index, "category": category, "source_span": text, "negative_error_control": category in NEGATIVES})
                    negative_blocks += category in NEGATIVES
                    adversarial_blocks += category in ADVERSARIAL
                    positive_error_blocks += any(label[1] == "incorrect" for label in labels)
                    for family, outcome, evidence_type, issue_kind in labels:
                        outcome_counts[outcome] += 1
                        gold.append({"source_span": text, "learner_utterance": u,
                                     # Wrong teacher suggestions must not become a learner correction.
                                     "corrected_form": c if outcome == "incorrect" else None,
                                     "teacher_comment": None, "construction": family,
                                     "outcome": outcome, "production_mode": mode, "evidence_type": evidence_type,
                                     "issue_kind": issue_kind,
                                     "feature": "question" if u.endswith("?") else "negative" if " not " in u or "n't" in u else "affirmative"})
                raw = f"# Speaking session {sid}\n\nWe talked about work, travel and past experiences. The notes below preserve exact quotes.\n\n" + "\n\n".join(blocks) + "\n"
                (directory / f"{sid}.md").write_text(raw, encoding="utf-8")
                gold_path = directory / f"{sid}.gold.json"
                gold_path.write_text(json.dumps({"session_id": sid, "dataset_version": VERSION, "observations": gold, "blocks": block_info}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                total_gold += len(gold)
                for path in (directory / f"{sid}.md", gold_path):
                    checksums[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest["splits"][split] = {"sessions": 8, "narrative_blocks": 128, "gold_observations": total_gold,
                                    "negative_error_control_blocks": negative_blocks, "adversarial_blocks": adversarial_blocks,
                                    "blocks_with_gold_errors": positive_error_blocks, "gold_outcomes": outcome_counts,
                                    "sha256": checksums}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    summary = generate()
    print(json.dumps({k: {f: v for f, v in s.items() if f != "sha256"} for k, s in summary["splits"].items()}, indent=2))
