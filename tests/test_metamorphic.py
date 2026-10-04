import pytest

from thoth.adapters import OfflineAdapter
from thoth.contracts import Outcome
from thoth.pipeline import process

FIRST = 'During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I\'ve lived here since 2021." The situation still continues.'
SECOND = 'During prompted conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" This is a neutral question.'


def semantic(raw):
    return {(o.learner_utterance, o.construction, o.outcome.value, o.production_mode.value, o.evidence_type.value)
            for o in process(raw, "test", OfflineAdapter()).observations}


def test_irrelevant_text_invariance():
    assert semantic(FIRST) == semantic("Administrative reminder: next lesson on Monday.\n\n" + FIRST + "\n\nWe talked about hobbies.")


def test_ordering_independence():
    assert semantic(FIRST + "\n\n" + SECOND) == semantic(SECOND + "\n\n" + FIRST)


def test_provenance_preserved_with_formatting():
    raw = "# Notes\n\n- [00:31] " + FIRST.replace("The teacher", "The\n teacher")
    result = process(raw, "test", OfflineAdapter())
    assert result.observations
    for o in result.observations:
        assert o.learner_utterance in raw[o.source_start:o.source_end]


def test_explicit_correction_removal_never_invents_correction():
    raw = FIRST.split(" The teacher")[0]
    result = process(raw, "test", OfflineAdapter())
    assert not any(o.corrected_form for o in result.observations)
    assert not any(o.outcome == Outcome.correct for o in result.observations)


def test_teacher_only_sentence_not_attributed():
    assert not semantic(FIRST.replace("the learner said", "the teacher explained"))


def test_noise_does_not_create_errors():
    assert semantic(FIRST) == semantic("[10:00] - " + FIRST + "\n\n# Attendance\n- Fee paid.\n- Sound was clear.")


@pytest.mark.parametrize("utterance,correction,note", [
    ("I think this implementation is good.", "I think this is a solid implementation.", "A more natural stylistic suggestion."),
    ("I've lived here since 2021.", "I live here since 2021.", "The situation still continues. The teacher was mistaken."),
    ("I worked there for three years.", None, "This is an ended job; I no longer work there."),
])
def test_no_grammar_failure_for_style_wrong_teacher_or_ended_context(utterance, correction, note):
    raw = f'During spontaneous conversation, the learner said: "{utterance}" '
    if correction:
        raw += f'The teacher corrected this to: "{correction}" '
    raw += note
    assert not any(o.outcome == Outcome.incorrect for o in process(raw, "test", OfflineAdapter()).observations)


def test_regression_multiple_errors_do_not_make_valid_tense_fail():
    raw = 'During spontaneous conversation, the learner said: "I have lived here since three years." The teacher corrected this to: "I have lived here for three years." The tense is valid; the time preposition needs repair.'
    observations = process(raw, "test", OfflineAdapter()).observations
    outcomes = {o.construction: o.outcome for o in observations}
    assert outcomes["present_perfect.duration"] == Outcome.correct
    assert outcomes["duration.since_for"] == Outcome.incorrect
