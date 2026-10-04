from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from thoth.contracts import Observation, PipelineResult, digest
from thoth.provenance import normalized, validate


class Store:
    """Append-only sources and runs; one active extraction per session."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.db.close()
            raise ValueError(f"Unsupported database version {version}")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, raw TEXT NOT NULL, source_name TEXT NOT NULL,
                occurred_on TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                pipeline_id TEXT NOT NULL, created_at TEXT NOT NULL,
                result_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS active_runs (
                session_id TEXT PRIMARY KEY REFERENCES sessions(id),
                run_id TEXT NOT NULL UNIQUE REFERENCES runs(id));
            CREATE TRIGGER IF NOT EXISTS preserve_sessions_update BEFORE UPDATE ON sessions
                BEGIN SELECT RAISE(ABORT, 'raw sessions are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_sessions_delete BEFORE DELETE ON sessions
                BEGIN SELECT RAISE(ABORT, 'raw sessions are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_runs_update BEFORE UPDATE ON runs
                BEGIN SELECT RAISE(ABORT, 'extraction runs are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_runs_delete BEFORE DELETE ON runs
                BEGIN SELECT RAISE(ABORT, 'extraction runs are immutable'); END;
            PRAGMA user_version=1;
        """)

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def save_session(self, raw: str, source_name: str, occurred_on: str) -> str:
        date.fromisoformat(occurred_on)
        if not raw.strip():
            raise ValueError("Session input is empty")
        session_id = "SES-" + digest(raw)[:20]
        existing = self.db.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
        if existing:
            if existing["raw"] != raw or existing["occurred_on"] != occurred_on:
                raise ValueError("Existing source/date differs; cannot silently replace session metadata")
            return session_id
        with self.db:
            self.db.execute("INSERT INTO sessions VALUES (?,?,?,?,?)",
                            (session_id, raw, source_name, occurred_on, datetime.now(timezone.utc).isoformat()))
        return session_id

    def session(self, session_id: str) -> dict:
        row = self.db.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
        if row is None:
            raise ValueError("Session not found")
        return dict(row)

    def save_run(self, session_id: str, result: PipelineResult) -> str:
        source = self.session(session_id)
        for o in result.observations:
            if o.session_id != session_id or o.pipeline_id != result.pipeline["pipeline_id"]:
                raise ValueError("Observation has mismatched source/pipeline")
            span = validate(source["raw"], o.source_span, o.learner_utterance, o.corrected_form, o.teacher_comment)
            if span != (o.source_start, o.source_end):
                raise ValueError("Stored source offsets do not match raw source")
            if not (o.source_start <= o.learner_start < o.learner_end <= o.source_end) or normalized(source["raw"][o.learner_start:o.learner_end]) != normalized(o.learner_utterance):
                raise ValueError("Stored learner quote offsets do not match raw source")
        run_id = "RUN-" + uuid.uuid4().hex[:20]
        with self.db:
            self.db.execute("INSERT INTO runs VALUES (?,?,?,?,?)",
                            (run_id, session_id, result.pipeline["pipeline_id"],
                             datetime.now(timezone.utc).isoformat(), result.model_dump_json()))
            self.db.execute("INSERT INTO active_runs VALUES (?,?) ON CONFLICT(session_id) DO UPDATE SET run_id=excluded.run_id",
                            (session_id, run_id))
        return run_id

    def history(self, session_id: str) -> list[dict]:
        return [dict(row) for row in self.db.execute(
            "SELECT r.id,r.pipeline_id,r.created_at, a.run_id=r.id AS active FROM runs r "
            "LEFT JOIN active_runs a ON a.session_id=r.session_id WHERE r.session_id=? ORDER BY r.created_at,r.id",
            (session_id,))]

    def active(self) -> tuple[list[Observation], dict[str, dict]]:
        observations, sessions = [], {}
        rows = self.db.execute("SELECT s.*,r.result_json FROM sessions s JOIN active_runs a ON a.session_id=s.id "
                               "JOIN runs r ON r.id=a.run_id ORDER BY s.occurred_on,s.id")
        for row in rows:
            source = dict(row)
            result = PipelineResult.model_validate_json(source.pop("result_json"))
            for o in result.observations:
                offsets = validate(source["raw"], o.source_span, o.learner_utterance, o.corrected_form, o.teacher_comment)
                if offsets != (o.source_start, o.source_end):
                    raise ValueError("Persisted provenance failed validation")
                if not (o.source_start <= o.learner_start < o.learner_end <= o.source_end) or normalized(source["raw"][o.learner_start:o.learner_end]) != normalized(o.learner_utterance):
                    raise ValueError("Persisted learner quote offsets failed validation")
            observations.extend(result.observations)
            sessions[source["id"]] = source
        return observations, sessions
