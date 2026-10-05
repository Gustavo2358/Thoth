import json
import sqlite3
from pathlib import Path

import httpx
import numpy as np
import pytest
from pydantic import ValidationError

from thoth import prompts
from thoth.artifacts import export
from thoth.benchmark import score
from thoth.contracts import Evidence, Extraction, Observation, Policy, Resolution, Review, digest
from thoth.embeddings import LocalEmbedder, blob, pedagogical_text, unblob
from thoth.engine import learner_state
from thoth.llm import ManualChatGPTAdapter, OpenAIAdapter, PendingResponse, payload
from thoth.pipeline import candidates, ingest, resolve
from thoth.provenance import locate
from thoth.storage import Store
from thoth.cli import main

POLICY = Policy(neighbors=2, pattern_dates=2, practice_dates=3)


def fixture(number, mode="spontaneous", performance="difficulty", kind="observed_use", review="keep"):
    from thoth.conversation import parse, reference
    quote = "I am agree with that."
    teacher = 'Say: "I am agree with that."' if mode == 'controlled' else "Let's discuss your view."
    raw = f'# Conversation {number}\n\n## Assistant\n{teacher}\n\n## User\n{quote}\n'
    sid = "SES-" + digest(raw)[:16]
    ref = reference(raw, parse(raw), 2, quote, quote, 'learner')
    support = 'no_support' if mode == 'spontaneous' else 'immediate_repetition' if mode == 'controlled' else 'contextual_prompt' if mode == 'prompted' else 'unknown'
    o = Observation(source_excerpt=quote, learner_quote=quote, production_mode=mode, turn=2,
        support=support, support_turns=[1] if mode in {'prompted','controlled'} else [],
        performance=performance, evidence_type=kind, communicative_intent="State agreement",
        learning_dimension="Expressing agreement naturally", observed_behavior="Produced an agreement expression",
        suggested_forms=["I agree."], hypothesis=None, id=f"OBS-{number}", session_id=sid,
        **{k:ref[k] for k in ('source_start','source_end','source_line_start','source_line_end')},
        review=Review(decision=review, reason="Test evidence"))
    return raw, o


def decision(category="new_pattern", candidate=None):
    return Resolution(decision=category, candidate_id=candidate, reason="Same ability" if candidate else "No prior comparable evidence",
                      pattern_label="Expressing agreement" if category == "same_pattern" else None,
                      pattern_description="Observed agreement expressions; mental cause remains unknown" if category == "same_pattern" else None,
                      conversation_contexts=["Discuss a view you agree with"] if category == "same_pattern" else [])


def add(store, number, day, root=None, **kwargs):
    raw, o = fixture(number, **kwargs)
    prior = store.records()
    match = next((r for r in prior if r["root_id"] == root), None) if root else None
    d = decision("same_pattern", match["id"]) if match else decision()
    r = dict(id=o.id, session_id=o.session_id, observation=o, vector=np.array([1., 0.], dtype="<f4"),
             embedding_model="test", root_id=root or o.id, resolution=d, occurred_on=f"2026-01-{day:02d}")
    summaries = {root: (d.pattern_label, d.pattern_description, d.conversation_contexts)} if match else {}
    store.commit_session(raw, r["occurred_on"], [r], summaries, {}, POLICY)
    return r


def test_open_schema_and_unreported_alternatives_are_allowed():
    raw, o = fixture(1)
    assert "I agree." not in raw
    assert locate(raw, o.source_excerpt, o.learner_quote) == (o.source_start, o.source_end)
    Evidence.model_validate(o.model_dump(exclude={"id", "session_id", "source_start", "source_end", "source_line_start", "source_line_end", "review"}))
    with pytest.raises(ValidationError):
        Evidence.model_validate({**o.model_dump(exclude={"id", "session_id", "source_start", "source_end", "source_line_start", "source_line_end", "review"}), "construction": "closed-skill"})
    assert "difficulty" not in pedagogical_text(o)


@pytest.mark.parametrize("kind", ["opportunity", "self_correction"])
def test_nonattempt_evidence_cannot_be_failure(kind):
    with pytest.raises(ValidationError):
        fixture(1, kind=kind)


def test_provenance_is_traceability_not_audio_forensics():
    raw = 'The learner said: I have a doubt.'
    assert locate('🎙️\n' + raw, raw, 'I have a doubt.')[0] == 3
    with pytest.raises(ValueError):
        locate(raw + "\n" + raw, raw, 'I have a doubt.')
    with pytest.raises(ValueError):
        locate(raw, raw, "Not said")


def test_vector_blob_is_portable_and_rejects_invalid_vectors():
    v = np.array([.6, .8], dtype="<f4")
    assert np.array_equal(v, unblob(blob(v)))
    with pytest.raises(ValueError):
        blob(np.array([1., float("nan")]))


def test_real_local_embedding_shape_normalization_and_semantic_signal():
    m = LocalEmbedder()
    a, b, c = m.embed(["expressing uncertainty in conversation", "conveying personal uncertainty naturally",
                      "organizing a meeting with conventional verb combinations"])
    assert a.shape == (300,)
    assert np.linalg.norm(a) == pytest.approx(1)
    assert float(a @ b) > float(a @ c)
    assert m.metadata["weights_sha256"]


def test_similarity_one_does_not_force_same_membership():
    with Store(":memory:") as store:
        first = add(store, 1, 1)
        _, next_o = fixture(2)
        class Related:
            def call(self, *_):
                return decision("related_but_different", first["id"])
        d, root, retrieved = resolve(next_o, first["vector"], store.records(), {}, POLICY, Related())
        assert retrieved[0]["similarity"] == 1
        assert d.decision == "related_but_different"
        assert root == next_o.id


def test_resolver_cannot_select_unretrieved_evidence():
    with Store(":memory:") as store:
        first = add(store, 1, 1)
        _, next_o = fixture(2)
        class Invalid:
            def call(self, *_):
                return decision("same_pattern", "OBS-not-retrieved")
        with pytest.raises(ValueError, match="outside"):
            resolve(next_o, first["vector"], store.records(), {}, POLICY, Invalid())


def test_one_date_cannot_create_pattern_even_with_many_reports():
    with Store(":memory:") as store:
        add(store, 1, 1)
        for n in range(2, 7):
            add(store, n, 1, root="OBS-1")
        assert not store.patterns()
        state = learner_state(store, POLICY)
        assert len(state["isolated"]) == 6


def test_emergence_practice_and_recovery_preserve_positive_and_negative_history(tmp_path):
    with Store(tmp_path / "learner.db") as store:
        add(store, 1, 1)
        add(store, 2, 7, root="OBS-1")
        assert learner_state(store, POLICY)["patterns"][0]["status"] == "collect"
        add(store, 3, 14, root="OBS-1")
        assert learner_state(store, POLICY)["patterns"][0]["status"] == "practice"
        add(store, 4, 21, root="OBS-1", performance="successful")
        add(store, 5, 28, root="OBS-1", performance="successful")
        state = export(tmp_path / "packs", store, POLICY)
        pattern = state["patterns"][0]
        assert pattern["status"] == "recovery"
        assert pattern["modes"]["spontaneous"] == {"successful": 2, "difficulty": 3, "uncertain": 0}
        pack = (tmp_path / "packs" / "patterns" / (pattern["id"] + ".md")).read_text()
        assert all(f"OBS-{i}" in pack for i in range(1, 6))
        assert "Grouping:" in pack and "Conversation source" in pack
    with Store(tmp_path / "learner.db") as reopened:
        assert learner_state(reopened, POLICY) == state


def test_uncertainty_modes_opportunities_and_repairs_remain_separate():
    with Store(":memory:") as store:
        add(store, 1, 1)
        add(store, 2, 7, root="OBS-1", mode="controlled", performance="successful")
        add(store, 3, 14, root="OBS-1", kind="opportunity", performance="uncertain")
        add(store, 4, 21, root="OBS-1", kind="self_correction", performance="uncertain")
        p = learner_state(store, POLICY)["patterns"][0]
        assert p["modes"]["spontaneous"] == {"successful": 0, "difficulty": 1, "uncertain": 2}
        assert p["modes"]["controlled"]["successful"] == 1
        assert p["opportunities"] == p["self_corrections"] == 1
        assert p["status"] == "collect"
        assert "cause is unproven" in p["mode_note"]


def test_transactions_provenance_idempotency_and_source_immutability():
    with Store(":memory:") as store:
        r = add(store, 1, 1)
        raw, _ = fixture(1)
        assert store.existing(raw, "2026-01-01")
        with pytest.raises(ValueError):
            store.existing(raw, "2026-01-02")
        with pytest.raises(sqlite3.IntegrityError):
            store.db.execute("UPDATE sessions SET raw='changed'")
        raw, o = fixture(2)
        bad = {**r, "id": o.id, "observation": o, "root_id": "OBS-nonexistent", "resolution": decision()}
        with pytest.raises(ValueError, match="membership"):
            store.commit_session(raw, "2026-01-02", [bad], {}, {}, POLICY)
        assert len(store.sources()) == len(store.records()) == 1


def test_pending_manual_session_is_atomic(tmp_path):
    raw, o = fixture(1)
    class SmallEmbedder:
        model = "test"
        metadata = {}
        def embed(self, texts): return [np.array([1., 0.]) for _ in texts]
    class Waiting:
        trace = []
        def metadata(self): return {}
        def call(self, stage, *_):
            if stage == "extract":
                return Extraction(observations=[Evidence.model_validate(o.model_dump(exclude={"id", "session_id", "source_start", "source_end", "source_line_start", "source_line_end", "review"}))], teaching=[], goals=[])
            raise PendingResponse("Review not provided")
    with Store(tmp_path / "learner.db") as store:
        with pytest.raises(PendingResponse):
            ingest(raw, "2026-01-01", store, SmallEmbedder(), Waiting(), POLICY)
        assert not store.sources() and not store.records()


@pytest.mark.parametrize("raw", [b"not JSON", b'{"decision":"keep","reason":"ok","confidence":1}', b'{"decision":"keep"}'])
def test_manual_preserves_invalid_originals_and_uses_strict_contract(tmp_path, raw):
    adapter = ManualChatGPTAdapter(tmp_path, "named-model")
    with pytest.raises(PendingResponse):
        adapter.call("review", prompts.REVIEW, {"excerpt": "source"}, Review)
    case = next(tmp_path.glob("*/request.json")).parent
    (case / "response.txt").write_bytes(raw)
    with pytest.raises(ValueError):
        adapter.call("review", prompts.REVIEW, {"excerpt": "source"}, Review)
    assert (case / "response.txt").read_bytes() == raw
    assert (case / "validation.txt").exists()


def test_manual_response_tampering_and_import_are_detected(tmp_path):
    adapter = ManualChatGPTAdapter(tmp_path / "exchange", "model")
    with pytest.raises(PendingResponse):
        adapter.call("review", "prompt", {"source": "report"}, Review)
    case = next((tmp_path / "exchange").glob("*/request.json")).parent
    source = tmp_path / "answers"
    source.mkdir()
    (source / (case.name + ".txt")).write_text('{"decision":"keep","reason":"Supported"}')
    assert adapter.import_responses(source) == 1
    adapter.call("review", "prompt", {"source": "report"}, Review)
    (case / "response.txt").write_text('{"decision":"reject","reason":"Edited"}')
    with pytest.raises(ValueError, match="overwrite"):
        adapter.call("review", "prompt", {"source": "report"}, Review)


def test_api_and_manual_send_identical_logical_payload(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-not-a-secret")
    api = OpenAIAdapter("test-model")
    seen = {}
    class Client:
        def __init__(self, **_): pass
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def post(self, url, json, headers):
            seen.update(json)
            return httpx.Response(200, json={"choices":[{"finish_reason":"stop","message":{"content":'{"decision":"keep","reason":"Supported"}'}}]})
    monkeypatch.setattr(httpx, "Client", Client)
    assert api.call("review", "prompt", {"source":"report"}, Review).decision == "keep"
    logical = payload("prompt", {"source":"report"}, Review)
    assert seen["messages"] == logical["messages"]
    assert seen["response_format"] == logical["response_format"]


def test_pairwise_metrics_expose_false_merges_and_splits():
    records = [dict(id="a", root_id="x", occurred_on="2026-01-01"),
               dict(id="b", root_id="y", occurred_on="2026-01-02"),
               dict(id="c", root_id="x", occurred_on="2026-01-02")]
    gold = {"a":{"group":"one"}, "b":{"group":"one"}, "c":{"group":"two"}}
    m = score(records, {"patterns":[]}, gold, [])
    assert m["pairwise"]["false_merge_pairs"] == 1
    assert m["pairwise"]["false_split_pairs"] == 1
    assert m["missed_recurrences"] == ["one"]


def test_cli_starts_empty_without_loading_embeddings(tmp_path, monkeypatch):
    import thoth.cli
    monkeypatch.setattr(thoth.cli, "LocalEmbedder", lambda: (_ for _ in ()).throw(AssertionError("No embedding needed for state")))
    args = ["--db", str(tmp_path / "learner.db"), "--artifacts", str(tmp_path / "packs")]
    assert main(args + ["state"]) == 0
    assert main(args + ["patterns"]) == 0
    assert main(args + ["prepare"]) == 0
    state = json.loads((tmp_path / "packs" / "learner-state.json").read_text())
    assert state["observations"] == 0 and state["patterns"] == []
