from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

from thoth.contracts import Observation, Resolution, digest
from thoth.embeddings import blob, pedagogical_text, unblob
from thoth.provenance import locate


class Store:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, occurred_on TEXT NOT NULL, raw TEXT NOT NULL, audit TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                data TEXT NOT NULL, pedagogical_text TEXT NOT NULL, vector BLOB NOT NULL,
                embedding_model TEXT NOT NULL, root_id TEXT NOT NULL,
                resolution TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY, root_id TEXT NOT NULL UNIQUE,
                label TEXT NOT NULL, description TEXT NOT NULL, contexts TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS preserve_sessions BEFORE UPDATE ON sessions
                BEGIN SELECT RAISE(ABORT, 'sources are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_observations BEFORE UPDATE ON observations
                BEGIN SELECT RAISE(ABORT, 'evidence is immutable'); END;
        """)

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def existing(self, raw: str, occurred_on: str) -> bool:
        row = self.db.execute("SELECT * FROM sessions WHERE id=?", ("SES-" + digest(raw)[:16],)).fetchone()
        if row and row["occurred_on"] != occurred_on:
            raise ValueError("Same report already has a different date; distinguish separate lessons in the report")
        return row is not None

    def records(self) -> list[dict]:
        rows = self.db.execute("SELECT o.*,s.occurred_on FROM observations o JOIN sessions s ON s.id=o.session_id ORDER BY s.occurred_on,o.rowid")
        result = []
        for row in rows:
            record = dict(row)
            record["observation"] = Observation.model_validate_json(record.pop("data"))
            record["vector"] = unblob(record["vector"])
            record["resolution"] = Resolution.model_validate_json(record["resolution"])
            result.append(record)
        return result

    def patterns(self) -> dict:
        return {row["root_id"]: dict(row) for row in self.db.execute("SELECT * FROM patterns ORDER BY id")}

    def commit_session(self, raw, occurred_on, records, summaries, audit, policy):
        date.fromisoformat(occurred_on)
        if not raw.strip():
            raise ValueError("Empty session")
        if self.existing(raw, occurred_on):
            return
        sid = "SES-" + digest(raw)[:16]
        previous = self.records()
        known = {r["id"]: r for r in previous}
        prior_date = self.db.execute("SELECT MAX(occurred_on) FROM sessions").fetchone()[0]
        if prior_date and occurred_on < prior_date:
            raise ValueError("Ingest reports chronologically so semantic decisions have the correct history")
        with self.db:
            self.db.execute("INSERT INTO sessions VALUES (?,?,?,?)", (sid, occurred_on, raw, json.dumps(audit)))
            for record in records:
                o = record["observation"]
                if o.session_id != sid or locate(raw, o.source_excerpt, o.learner_quote) != (o.source_start, o.source_end):
                    raise ValueError("Observation provenance/source mismatch")
                decision = record["resolution"]
                if decision.candidate_id and decision.candidate_id not in known:
                    raise ValueError("Resolution refers to unknown evidence")
                expected_root = known[decision.candidate_id]["root_id"] if decision.decision == "same_pattern" else o.id
                if record["root_id"] != expected_root:
                    raise ValueError("Invalid membership root")
                self.db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)",
                                (o.id, sid, o.model_dump_json(), pedagogical_text(o), blob(record["vector"]),
                                 record["embedding_model"], record["root_id"], decision.model_dump_json()))
                known[o.id] = record
            all_records = previous + records
            groups = {}
            for record in all_records:
                groups.setdefault(record["root_id"], []).append(record)
            for root, members in groups.items():
                dates = {r["occurred_on"] for r in members if r["observation"].review.decision == "keep"}
                if len(dates) >= policy.pattern_dates and root in summaries:
                    label, description, contexts = summaries[root]
                    self.db.execute("INSERT INTO patterns VALUES (?,?,?,?,?) ON CONFLICT(root_id) DO UPDATE SET label=excluded.label,description=excluded.description,contexts=excluded.contexts",
                                    ("PAT-" + root.removeprefix("OBS-")[:12], root, label, description, json.dumps(contexts)))

    def sources(self):
        return [dict(row) for row in self.db.execute("SELECT * FROM sessions ORDER BY occurred_on,id")]
