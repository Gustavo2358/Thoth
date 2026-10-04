import json
from pathlib import Path

import pytest

from thoth.artifacts import write_json
from thoth.engine import aggregate, lesson_targets
from thoth.profile_benchmark import materialize, metadata, run

DATASET = Path("benchmark/profiles.json")


def test_development_decisions_against_preregistered_profiles(tmp_path):
    # No holdout execution in the routine suite: preserve it for frozen qualification.
    report = run(DATASET, "development", tmp_path / "development")
    assert report["decision_suite_passed"], [(r["id"], [c["name"] for c in r["checks"] if not c["passed"]])
                                            for r in report["results"] if not r["passed"]]
    assert report["primary"]["false_positives"] == 0
    assert report["primary"]["false_negatives"] == 0
    assert report["learning_gain"] == "NOT_MEASURED"
    assert report["real_student_readiness"] == "NOT_ESTABLISHED"
    with pytest.raises(ValueError, match="previous profile evaluations"):
        run(DATASET, "development", tmp_path / "development")


def test_profile_freeze_rejects_modified_expectations_before_holdout(tmp_path):
    dataset = tmp_path / "profiles.json"
    dataset.write_bytes(DATASET.read_bytes())
    freeze = tmp_path / "freeze.json"
    write_json(freeze, metadata(dataset))
    data = json.loads(dataset.read_bytes())
    data["profiles"][-1]["expected"]["primary"] = ["article.indefinite"]
    write_json(dataset, data)
    with pytest.raises(ValueError, match="Freeze the implementation"):
        run(dataset, "holdout", tmp_path / "holdout", freeze)
    assert not (tmp_path / "holdout").exists()


def test_temporal_halves_cannot_split_reports_from_same_date():
    # Four dates, very unequal number of reports per date. Session-count halves
    # falsely report a stable trend; date halves correctly retain the recovery.
    family = "present_perfect.duration"
    profile = dict(id="temporal-boundary", sessions=[])
    for day, pattern, reports in [(0, "FFF", 1), (7, "FFF", 1), (14, "SSS", 8), (21, "SSS", 1)]:
        profile["sessions"] += [dict(day=day, runs=[dict(family=family, outcomes=pattern,
                                                       mode="spontaneous", feature="affirmative")]) for _ in range(reports)]
    fixtures = materialize(profile)
    observations = [o for s in fixtures for o in s["observations"]]
    sessions = {s["id"]: s for s in fixtures}
    state = aggregate(observations, sessions)
    assert state["constructions"][family]["trend"]["label"] == "improving"
    assert state["constructions"][family]["trend"]["early_accuracy"] == 0
    assert state["constructions"][family]["trend"]["recent_accuracy"] == 1
    assert lesson_targets(state)["primary"] == []


def test_corrupt_target_expectation_is_reported_as_failure(tmp_path):
    data = json.loads(DATASET.read_bytes())
    # The engine must not be able to pass by copying fixture expectations.
    case = next(p for p in data["profiles"] if p["id"] == "D05-clustered-errors")
    case["expected"]["primary"] = ["present_perfect.duration"]
    data["profiles"] = [case]
    dataset = tmp_path / "deliberately-wrong-gold.json"
    write_json(dataset, data)
    report = run(dataset, "development", tmp_path / "result")
    assert not report["decision_suite_passed"]
    assert report["primary"]["false_negatives"] == 1
