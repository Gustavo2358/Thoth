import io
import json
from pathlib import Path

import httpx
import pytest

from thoth.adapters import OpenAIAdapter, adapter
from thoth.benchmark import dataset_metadata, freeze, qualify, run_split
from thoth.cli import main
from thoth.contracts import Extraction, Proposal, Verdict
from thoth.llm import InvalidLLMResponse, PendingLLMResponse, structured_payload
from thoth.manual_adapter import ManualChatGPTAdapter
from thoth.pipeline import process
from thoth.prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT
from thoth.contracts import TAXONOMY

ROOT = Path(__file__).resolve().parents[1]
RAW = 'During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" This is a neutral direct question.'


def proposed():
    return Proposal(source_span=RAW, learner_utterance="Where you work?", corrected_form="Where do you work?",
                    construction="question.do_support", outcome="incorrect", production_mode="spontaneous",
                    evidence_type="explicit_correction", issue_kind="grammar", feature="question")


def latest_entry(manual):
    return json.loads((manual.directory / "exchange.json").read_bytes())["requests"][-1]


def import_answer(manual, tmp_path, entry, raw):
    directory = tmp_path / "incoming"
    directory.mkdir(exist_ok=True)
    for p in directory.iterdir():
        p.unlink()
    (directory / entry["filename"]).write_bytes(raw)
    return manual.import_responses(directory)


def test_manual_and_api_use_identical_logical_payloads(monkeypatch, tmp_path):
    monkeypatch.setenv("THOTH_API_KEY", "unit-test-placeholder")
    monkeypatch.delenv("THOTH_BASE_URL", raising=False)
    captured = []
    real_client = httpx.Client

    def handle(request):
        body = json.loads(request.content)
        captured.append({k: v for k, v in body.items() if k not in {"model", "temperature"}})
        answer = {"observations": []} if len(captured) == 1 else {"decision": "uncertain", "reason": "Test response"}
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(answer)}}]})

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: real_client(transport=httpx.MockTransport(handle), **kwargs))
    api = OpenAIAdapter("test-model")
    manual = ManualChatGPTAdapter(tmp_path / "exchange", model="ChatGPT test label")
    api.extract(RAW)
    with pytest.raises(PendingLLMResponse):
        manual.extract(RAW)
    api.verify(proposed())
    with pytest.raises(PendingLLMResponse):
        manual.verify(proposed())
    manual_requests = [json.loads((manual.directory / "cases" / e["request_sha256"] / "request.json").read_bytes())
                       for e in manual._manifest()["requests"]]
    assert [r["logical_payload"] for r in manual_requests] == captured
    assert manual_requests[0]["metadata"]["mode"] == "manual-chat"
    for request in manual_requests:
        assert "gold" not in request and "learner_state" not in request


@pytest.mark.parametrize("original", [b'not JSON\r\n', b'```json\n{"observations": []}\n```\n',
                                       b'{"observations": [], "confidence": .99}', b''])
def test_original_invalid_response_is_preserved_and_cannot_be_repaired(tmp_path, original):
    manual = ManualChatGPTAdapter(tmp_path / "exchange")
    with pytest.raises(PendingLLMResponse):
        manual.extract(RAW)
    entry = latest_entry(manual)
    result = import_answer(manual, tmp_path, entry, original)
    assert result == {"imported": 1, "invalid": 1}
    case = manual.directory / "cases" / entry["request_sha256"]
    assert (case / "response.txt").read_bytes() == original
    assert json.loads((case / "validation.json").read_bytes())["status"] == "invalid"
    assert not (case / "parsed.json").exists()
    with pytest.raises(InvalidLLMResponse):
        manual.extract(RAW)
    with pytest.raises(ValueError, match="overwrite"):
        import_answer(manual, tmp_path, entry, b'{"observations": []}')
    assert (case / "response.txt").read_bytes() == original


def test_manual_interactive_eof_is_supported_and_raw_is_not_reformatted(monkeypatch, tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange", interactive=True)
    original = '{\n  "observations": []\n}\n'
    monkeypatch.setattr("sys.stdin", io.StringIO(original))
    extracted, trace = manual.extract(RAW)
    assert not extracted.observations
    assert (Path(trace["case_directory"]) / "response.txt").read_bytes() == original.encode()


def test_manual_export_import_pipeline_round_trip_and_tamper_detection(tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange", model="ChatGPT / selected", export_directory=tmp_path / "requests")
    with pytest.raises(PendingLLMResponse):
        process(RAW, "s", manual)
    entry = latest_entry(manual)
    assert (tmp_path / "requests" / entry["filename"]).exists()
    original = json.dumps({"observations": [proposed().model_dump(mode="json")]}, indent=3).encode() + b"\r\n"
    import_answer(manual, tmp_path, entry, original)
    with pytest.raises(PendingLLMResponse):
        process(RAW, "s", manual)
    verifier_entry = latest_entry(manual)
    assert verifier_entry["stage"] == "Verdict"
    import_answer(manual, tmp_path, verifier_entry, b'{"decision":"supported","reason":"Do is required in this neutral direct question."}\n')
    result = process(RAW, "s", manual)
    assert len(result.observations) == 1 and result.observations[0].outcome.value == "incorrect"
    assert result.pipeline["mode"] == "manual-chat"
    case = manual.directory / "cases" / entry["request_sha256"]
    assert (case / "response.txt").read_bytes() == original
    (case / "response.txt").write_bytes(b'{"observations": []}')
    with pytest.raises(ValueError, match="modified"):
        manual.extract(RAW)


def test_manual_model_change_requires_separate_exchange(tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange", model="ChatGPT A")
    with pytest.raises(PendingLLMResponse):
        manual.extract(RAW)
    with pytest.raises(ValueError, match="different model"):
        ManualChatGPTAdapter(tmp_path / "exchange", model="ChatGPT B").extract(RAW)


def test_manual_enforces_required_keys_from_same_strict_api_schema(tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange")
    with pytest.raises(PendingLLMResponse):
        manual.extract(RAW)
    incomplete = proposed().model_dump(mode="json")
    del incomplete["teacher_comment"]
    original = json.dumps({"observations": [incomplete]}).encode()
    assert import_answer(manual, tmp_path, latest_entry(manual), original)["invalid"] == 1
    case = manual.directory / "cases" / latest_entry(manual)["request_sha256"]
    errors = json.loads((case / "validation.json").read_bytes())["errors"]
    assert errors[0]["type"] == "missing" and errors[0]["loc"] == ["observations", 0, "teacher_comment"]


def test_benchmark_pending_not_scored_invalid_json_is_scored_and_archived(tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange")
    manifest, _ = dataset_metadata(ROOT / "benchmark")
    records, metrics = run_split(ROOT / "benchmark", "development", manual, manifest, tmp_path / "cases")
    assert metrics["case_counts"] == {"completed": 0, "invalid": 0, "pending": 8}
    assert metrics["precision"] is None and metrics["false_negatives"] == 0 and metrics["scored_sessions"] == 0
    entry = manual._manifest()["requests"][0]
    import_answer(manual, tmp_path, entry, b'original malformed answer\n')
    records, metrics = run_split(ROOT / "benchmark", "development", manual, manifest, tmp_path / "cases")
    assert metrics["case_counts"] == {"completed": 0, "invalid": 1, "pending": 7}
    assert metrics["schema_validation_failed_cases"] == 1
    assert metrics["false_negatives"] == 18  # First half includes two multi-construction cases.
    invalid = next(r for r in records if r["status"] == "invalid")
    archive = tmp_path / "cases" / invalid["session_id"]
    assert (archive / "response.txt").read_bytes() == b'original malformed answer\n'
    assert (archive / "gold.json").exists() and (archive / "metadata.json").exists()
    assert json.loads((archive / "result.json").read_bytes())["status"] == "invalid"


def test_all_needed_verifier_prompts_are_exported_in_one_pass(tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange")
    second = proposed().model_copy(update={"construction": "auxiliary.chain"})
    with pytest.raises(PendingLLMResponse):
        manual.extract(RAW)
    import_answer(manual, tmp_path, latest_entry(manual), json.dumps({"observations": [proposed().model_dump(mode="json"), second.model_dump(mode="json")]}).encode())
    with pytest.raises(PendingLLMResponse):
        process(RAW, "s", manual)
    assert [r["stage"] for r in manual._manifest()["requests"]] == ["Extraction", "Verdict", "Verdict"]


def test_cli_manual_default_and_file_benchmark_without_api(monkeypatch, tmp_path):
    monkeypatch.delenv("THOTH_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert main(["benchmark", "--dataset", str(ROOT / "benchmark"), "--responses-dir", str(tmp_path / "exchange"),
                 "--export", str(tmp_path / "requests"), "--output", str(tmp_path / "reports")]) == 2
    assert len(list((tmp_path / "requests").glob("*.txt"))) == 8
    assert all("=== OUTPUT CONTRACT ===" in p.read_text() for p in (tmp_path / "requests").glob("*.txt"))
    assert isinstance(adapter("manual", responses_dir=tmp_path / "other"), ManualChatGPTAdapter)


def test_pending_qualification_does_not_publish_final_or_calibration(tmp_path):
    manual = ManualChatGPTAdapter(tmp_path / "exchange", model="ChatGPT / selected", evaluation_design="independent")
    freeze_path = tmp_path / "freeze.json"
    freeze(ROOT / "benchmark", manual, freeze_path)
    report = qualify(ROOT / "benchmark", tmp_path / "reports", manual, freeze_path)
    assert report["status"] == "pending" and report["phase"] == "calibration"
    assert not (tmp_path / "reports" / "benchmark-final.json").exists()
    assert not list((tmp_path / "reports").glob("runs/*/calibration.json"))
