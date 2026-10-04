import json
from pathlib import Path

import pytest

from thoth.adapters import OfflineAdapter
from thoth.benchmark import check_dataset, dataset_metadata, freeze, run_split
from thoth.contracts import digest
from thoth.evaluation import evaluate, score_session

ROOT = Path(__file__).resolve().parents[1]


def test_development_dataset_manifest_and_nonzero_test_count():
    manifest, metadata = dataset_metadata(ROOT / "benchmark")
    records, metrics = run_split(ROOT / "benchmark", "development", OfflineAdapter(), manifest)
    assert len(records) == 8 and metrics["gold_observations"] == 128
    assert metrics["accepted_hallucinated_provenance"] == 0
    assert metrics["negative_blocks_with_false_error"] == 0
    assert set(metrics["by_construction"]) >= {"present_perfect.duration", "article.indefinite"}
    assert metrics["grammar_attempt_metrics"]["tp"] > 60


def test_occurrence_sensitive_matching_does_not_mix_identical_quotes():
    gold = {"learner_start": 100, "learner_utterance": "I worked there for five years.",
            "construction": "present_perfect.duration", "outcome": "correct"}
    wrong_location = {**gold, "learner_start": 10}
    metrics, correctness = score_session([wrong_location], [gold])
    assert metrics["false_positives"] == 1 and metrics["false_negatives"] == 1


def test_freeze_checks_pipeline_and_dataset_without_running_holdout(tmp_path):
    path = tmp_path / "freeze.json"
    first = freeze(ROOT / "benchmark", OfflineAdapter(), path)
    assert freeze(ROOT / "benchmark", OfflineAdapter(), path) == first
    modified = json.loads(path.read_text())
    modified["pipeline"]["pipeline_id"] = "changed"
    path.write_text(json.dumps(modified))
    with pytest.raises(ValueError):
        freeze(ROOT / "benchmark", OfflineAdapter(), path)


def test_corrupt_dataset_is_rejected(tmp_path):
    directory = tmp_path / "datasets" / "development"
    directory.mkdir(parents=True)
    (directory / "unknown.md").write_text("extra")
    with pytest.raises(ValueError, match="differs"):
        check_dataset(tmp_path, {"splits": {"development": {"sha256": {}}}}, "development")
