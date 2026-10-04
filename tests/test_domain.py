import json
import sqlite3
from pathlib import Path

import pytest
from pydantic import ValidationError

from thoth.adapters import OfflineAdapter, OpenAIAdapter
from thoth.artifacts import export_learner, export_session
from thoth.cli import main
from thoth.contracts import Extraction, Proposal, Verdict, digest
from thoth.engine import aggregate, lesson_targets, posterior
from thoth.evaluation import calibrate, evaluate, match_key, score_session, validate_calibration
from thoth.pipeline import pipeline_metadata, process
from thoth.provenance import locate, validate
from thoth.storage import Store
from thoth.text_adapter import PendingResponse, TextAdapter


RAW = ('During spontaneous conversation, the learner said: "I live here since 2021." '
       'The teacher corrected this to: "I\'ve lived here since 2021." The situation still continues.')
GOOD = 'During spontaneous conversation, the learner said: "I\'ve worked here for three years." The sentence was correct.'


def proposal(**changes):
    return Proposal.model_validate({"source_span": RAW, "learner_utterance": "I live here since 2021.",
                                    "corrected_form": "I've lived here since 2021.", "teacher_comment": None,
                                    "construction": "present_perfect.duration", "feature": "affirmative",
                                    "outcome": "incorrect", "production_mode": "spontaneous",
                                    "evidence_type": "explicit_correction", "issue_kind": "grammar", **changes})


class Fake:
    def __init__(self, proposals, decision="supported"):
        self.proposals, self.decision = proposals, decision
        self.calls = 0

    def metadata(self):
        return {"provider": "fake", "model": "fixture", "verifier_model": "fixture"}

    def extract(self, raw):
        e = Extraction(observations=self.proposals)
        return e, {"stage": "Extraction", "response": e.model_dump(mode="json")}

    def verify(self, p):
        self.calls += 1
        v = Verdict(decision=self.decision, reason="Fixture verdict")
        return v, {"stage": "Verdict", "response": v.model_dump(mode="json")}


def test_schema_rejects_confidence_and_bad_enum():
    with pytest.raises(ValidationError):
        proposal(confidence=.99)
    with pytest.raises(ValidationError):
        proposal(outcome="probably")
    with pytest.raises(ValidationError):
        Extraction.model_validate_json('{"observations": [], "prose": "trust me"}')


def test_literal_provenance_whitespace_and_unicode_offsets():
    raw = "🎙️\n" + RAW.replace("The teacher", "The\n\tteacher")
    a, b = validate(raw, RAW, "I live here since 2021.", "I've lived here since 2021.")
    assert a == len("🎙️\n") and b == len(raw)
    with pytest.raises(ValueError):
        validate(raw, RAW, "I live here since 2022.")
    with pytest.raises(ValueError):
        validate(raw, RAW, "I live here since 2021.", "I have lived here for years.")
    with pytest.raises(ValueError):
        locate(RAW + "\n" + RAW, RAW)


def test_hallucinated_utterance_rejected_before_verifier():
    fake = Fake([proposal(learner_utterance="I work in Paris.")])
    result = process(RAW, "s", fake)
    assert not result.observations and len(result.rejected) == 1 and fake.calls == 0


def test_duplicate_proposals_rejected():
    result = process(RAW, "s", Fake([proposal(), proposal()]))
    assert len(result.observations) == 1 and result.rejected[0].reason.startswith("duplicate")


def test_duplicate_nested_source_spans_are_same_attempt():
    expanded = "Narrative intro. " + RAW
    result = process(expanded, "s", Fake([proposal(source_span=expanded), proposal()]))
    assert len(result.observations) == 1


def test_unknown_classification_and_uncertain_verifier_do_not_count():
    result = process(RAW, "s", Fake([proposal(construction="free form")]))
    assert result.observations[0].construction == "unclassified"
    assert result.observations[0].outcome.value == "uncertain"
    unresolved = process(RAW, "s", Fake([proposal()], "uncertain"))
    state = aggregate(unresolved.observations, {"s": {"occurred_on": "2026-01-01"}})
    assert state["constructions"]["present_perfect.duration"]["modes"]["spontaneous"]["attempts"] == 0


def test_deterministic_scores_are_not_llm_values():
    result = process(RAW, "s", Fake([proposal()]))
    o = result.observations[0]
    assert o.raw_support_score == 4 == sum(o.support_signals.values())
    assert "confidence" not in o.model_dump()


def test_unsupported_verifier_rejects():
    assert not process(RAW, "s", Fake([proposal()], "unsupported")).observations


def test_posterior_known_values_and_uncertainty():
    p = posterior(11, 5)
    assert p["alpha"] == 12 and p["beta"] == 6
    assert p["posterior_mean"] == pytest.approx(2/3)
    assert posterior(0, 0)["credible_interval_95"] == pytest.approx([.025, .975])
    width = lambda stats: stats["credible_interval_95"][1] - stats["credible_interval_95"][0]
    assert width(posterior(20, 20)) < width(posterior(1, 1))
    with pytest.raises(ValueError):
        posterior(-1, 0)


def test_mode_separation_determinism_and_sparse_trend():
    first = process(RAW, "a", OfflineAdapter()).observations
    second = process(GOOD.replace("spontaneous", "prompted"), "b", OfflineAdapter()).observations
    sessions = {"a": {"occurred_on": "2026-01-01"}, "b": {"occurred_on": "2026-01-02"}}
    left = aggregate(first + second, sessions)
    assert left == aggregate(second + first, sessions)
    entry = left["constructions"]["present_perfect.duration"]
    assert entry["modes"]["spontaneous"]["failures"] == 1
    assert entry["modes"]["prompted"]["successes"] == 1
    assert entry["trend"]["label"] == "insufficient_data"
    assert lesson_targets(left)["primary"] == []


@pytest.mark.parametrize("late_successes,expected", [(6, "improving"), (0, "stable")])
def test_trend_explicit_halves(late_successes, expected):
    observations, sessions = [], {}
    base = process(RAW, "s", OfflineAdapter()).observations[0]
    for session in range(4):
        sid = f"s{session}"
        sessions[sid] = {"occurred_on": f"2026-01-0{session+1}"}
        for attempt in range(3):
            good = session >= 2 and late_successes == 6
            observations.append(base.model_copy(update={"id": f"{sid}-{attempt}", "session_id": sid,
                                                        "outcome": type(base.outcome)("correct" if good else "incorrect")}))
    state = aggregate(observations, sessions)
    assert state["constructions"]["present_perfect.duration"]["trend"]["label"] == expected
    # Improvement leaves errors on only one of the last three attempt dates;
    # historical errors alone must not keep a construction in primary practice.
    assert lesson_targets(state)["primary"] == ([] if late_successes else ["present_perfect.duration"])


def test_opportunities_and_self_repairs_not_failures():
    raws = ['During prompted conversation, the learner said: "I started three years ago." This was an opportunity; target was not selected.',
            'During spontaneous conversation, the learner said: "I work... sorry, I\'ve worked here since 2022."']
    obs = sum([process(raw, str(i), OfflineAdapter()).observations for i, raw in enumerate(raws)], [])
    entry = aggregate(obs, {str(i): {"occurred_on": "2026-01-01"} for i in range(2)})["constructions"]["present_perfect.duration"]
    assert entry["opportunities"] == 1 and entry["self_corrections"] == 1
    assert all(v["attempts"] == 0 for v in entry["modes"].values())


def test_persistence_reprocessing_and_immutability(tmp_path):
    with Store(tmp_path / "app.db") as store:
        sid = store.save_session(RAW, "s.md", "2026-01-01")
        assert store.save_session(RAW, "s.md", "2026-01-01") == sid
        with pytest.raises(ValueError):
            store.save_session(RAW, "s.md", "2026-01-02")
        first = process(RAW, sid, OfflineAdapter())
        run1 = store.save_run(sid, first)
        export_session(tmp_path / "out", store.session(sid), run1, first)
        second = process(RAW, sid, Fake([], "supported"))
        run2 = store.save_run(sid, second)
        export_session(tmp_path / "out", store.session(sid), run2, second)
        assert len(store.history(sid)) == 2
        assert store.active()[0] == []
        assert (tmp_path / "out" / "sessions" / sid / "raw.md").read_text() == RAW
        assert (tmp_path / "out" / "sessions" / sid / "runs" / run1 / "audit.json").exists()
        with pytest.raises(sqlite3.IntegrityError):
            store.db.execute("UPDATE sessions SET raw='changed'")
        with pytest.raises(sqlite3.IntegrityError):
            store.db.execute("DELETE FROM runs")


def test_failed_reprocess_preserves_active_run(tmp_path):
    with Store(tmp_path / "app.db") as store:
        sid = store.save_session(RAW, "s.md", "2026-01-01")
        result = process(RAW, sid, OfflineAdapter())
        store.save_run(sid, result)
        tampered = result.model_copy(deep=True)
        tampered.observations[0].source_end += 1
        with pytest.raises(ValueError):
            store.save_run(sid, tampered)
        assert len(store.history(sid)) == 1 and len(store.active()[0]) == 1


def test_export_state_reconstructible_and_real_artifacts(tmp_path):
    result = process(RAW, "s", OfflineAdapter())
    metadata = {"s": {"occurred_on": "2026-01-01"}}
    state = export_learner(tmp_path, result.observations, metadata)
    assert json.loads((tmp_path / "learner" / "learner-state.json").read_text()) == aggregate(result.observations, metadata)
    assert state["observations"] == 1
    assert "Beta(1,1)" in (tmp_path / "learner" / "learner-state.md").read_text()
    assert result.observations[0].id in (tmp_path / "learner" / "evidence" / "present_perfect.duration.md").read_text()
    assert "Insufficient" in (tmp_path / "learner" / "next-lesson.md").read_text()


def test_reingest_preserves_crlf_raw_and_clears_stale_derived_packs(tmp_path):
    raw = RAW + "\r\n\r\nAdministrative notes.\r\n"
    file = tmp_path / "raw.md"
    file.write_bytes(raw.encode("utf-8"))
    flags = ["--db", str(tmp_path / "db.sqlite"), "--artifacts", str(tmp_path / "out")]
    assert main(flags + ["ingest", str(file), "--provider", "offline", "--date", "2026-01-01"]) == 0
    assert main(flags + ["ingest", str(file), "--provider", "offline"]) == 0
    with Store(tmp_path / "db.sqlite") as store:
        observations, sessions = store.active()
        assert next(iter(sessions.values()))["raw"] == raw
        sid = next(iter(sessions))
        assert (tmp_path / "out" / "sessions" / sid / "raw.md").read_bytes() == file.read_bytes()
    export_learner(tmp_path / "out", [], {})
    assert not (tmp_path / "out" / "learner" / "evidence" / "present_perfect.duration.md").exists()


def test_exact_matching_does_not_reward_similar_wrong_outcome():
    gold = proposal().model_dump(mode="json")
    wrong = {**gold, "outcome": "correct"}
    metrics, correctness = score_session([gold, gold, wrong], [gold])
    assert metrics["tp"] == 1 and metrics["false_positives"] == 2 and correctness == [True, False, False]
    assert match_key({**gold, "learner_utterance": "I  live\n here since 2021."}) == match_key(gold)
    assert match_key({**gold, "learner_utterance": "I live here since 2022."}) != match_key(gold)


def calibration_records():
    p = {**proposal().model_dump(mode="json"), "raw_support_score": 4}
    return [{"split": "calibration", "predictions": [p, {**p, "outcome": "correct"}], "correctness": [True, False]}]


def test_calibration_empirical_counts_and_pipeline_mismatch():
    pipeline = pipeline_metadata(OfflineAdapter())
    calibration = calibrate(calibration_records(), pipeline, {"version": "toy"})
    bucket = calibration["buckets"]["4"]
    assert bucket["observations"] == 2 and bucket["correct"] == 1 and bucket["empirical_precision"] == .5
    assert calibration["buckets"]["1"]["empirical_precision"] is None
    validate_calibration(calibration, pipeline)
    with pytest.raises(ValueError):
        validate_calibration(calibration, {"pipeline_id": "different"})
    with pytest.raises(ValueError):
        calibrate([{**calibration_records()[0], "split": "holdout_test"}], pipeline, {})


def test_cli_end_to_end_repeatable(tmp_path, capsys):
    raw_file = tmp_path / "s.md"
    raw_file.write_text(RAW)
    flags = ["--db", str(tmp_path / "app.db"), "--artifacts", str(tmp_path / "artifacts")]
    assert main(flags + ["ingest", str(raw_file), "--provider", "offline", "--date", "2026-01-01"]) == 0
    before = (tmp_path / "artifacts" / "learner" / "learner-state.json").read_bytes()
    assert main(flags + ["ingest", str(raw_file), "--provider", "offline"]) == 0
    assert before == (tmp_path / "artifacts" / "learner" / "learner-state.json").read_bytes()
    assert main(flags + ["state"]) == 0
    assert main(flags + ["next-lesson"]) == 0


def test_text_prompt_response_replay_and_binding(tmp_path):
    adapter = TextAdapter(tmp_path)
    with pytest.raises(PendingResponse):
        adapter.extract(RAW)
    request_path = next((tmp_path / "requests").iterdir())
    request = json.loads(request_path.read_text())
    assert "gold" not in request and "learner_state" not in request
    response_path = tmp_path / "responses" / request_path.name
    response_path.parent.mkdir()
    response_path.write_text(json.dumps({"request_sha256": request["request_sha256"], "response": {"observations": [proposal().model_dump(mode="json")]}}))
    extraction, trace = adapter.extract(RAW)
    assert len(extraction.observations) == 1 and trace["response_sha256"]
    response_path.write_text(json.dumps({"request_sha256": "bad", "response": {"observations": []}}))
    with pytest.raises(ValueError):
        adapter.extract(RAW)


def test_openai_adapter_missing_key_and_endpoint_security(monkeypatch):
    monkeypatch.delenv("THOTH_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="credential missing"):
        OpenAIAdapter()
    monkeypatch.setenv("THOTH_API_KEY", "local-test-value")
    monkeypatch.setenv("THOTH_BASE_URL", "http://remote.example/v1")
    with pytest.raises(ValueError, match="HTTPS"):
        OpenAIAdapter()


def test_openai_structured_contract_and_independent_prompt(monkeypatch):
    import httpx
    monkeypatch.setenv("THOTH_API_KEY", "local-test-value")
    requests = []
    real_client = httpx.Client

    def handle(req):
        body = json.loads(req.content)
        requests.append(body)
        schema_name = body["response_format"]["json_schema"]["name"]
        answer = {"observations": [proposal().model_dump(mode="json")]} if schema_name == "Extraction" else {"decision": "supported", "reason": "Source supports this"}
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(answer)}}]})

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: real_client(transport=httpx.MockTransport(handle), **kwargs))
    adapter = OpenAIAdapter("extract-model", "verify-model")
    result = process(RAW, "s", adapter)
    assert result.observations
    assert requests[0]["model"] == "extract-model" and requests[1]["model"] == "verify-model"
    assert requests[0]["messages"][0] != requests[1]["messages"][0]
    verify_input = json.loads(requests[1]["messages"][1]["content"])
    assert set(verify_input) == {"excerpt", "proposal"}
    schema = requests[0]["response_format"]["json_schema"]["schema"]["$defs"]["Proposal"]
    assert set(schema["required"]) == set(schema["properties"])
