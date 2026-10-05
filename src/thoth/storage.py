from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import date
from pathlib import Path

from thoth.contracts import Observation, Resolution, digest
from thoth.conversation import parse, reference
from thoth.embeddings import blob, pedagogical_text, unblob


class Store:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        # No experimental database migrations. A source can be replayed into a fresh DB.
        if self.db.execute("SELECT name FROM sqlite_master WHERE name='sessions'").fetchone():
            columns = {r[1] for r in self.db.execute('PRAGMA table_info(sessions)')}
            if 'source_sha256' not in columns:
                self.db.close()
                raise ValueError('Use a fresh database for conversation sources; experimental report databases are not supported')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, occurred_on TEXT NOT NULL, raw TEXT NOT NULL, source_sha256 TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS turns (
                session_id TEXT NOT NULL REFERENCES sessions(id), number INTEGER NOT NULL,
                speaker TEXT NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL,
                line_start INTEGER NOT NULL, line_end INTEGER NOT NULL,
                PRIMARY KEY(session_id, number));
            CREATE TABLE IF NOT EXISTS analyses (
                session_id TEXT PRIMARY KEY REFERENCES sessions(id), data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                data TEXT NOT NULL, pedagogical_text TEXT NOT NULL, vector BLOB NOT NULL,
                embedding_model TEXT NOT NULL, root_id TEXT NOT NULL, resolution TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY, root_id TEXT NOT NULL UNIQUE,
                label TEXT NOT NULL, description TEXT NOT NULL, contexts TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS teaching_directives (
                id TEXT PRIMARY KEY, instruction TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS teaching_evidence (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                data TEXT NOT NULL, refs TEXT NOT NULL,
                directive_id TEXT REFERENCES teaching_directives(id), decision TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY, text TEXT NOT NULL, session_id TEXT REFERENCES sessions(id), ref TEXT);
            CREATE TRIGGER IF NOT EXISTS preserve_sessions BEFORE UPDATE ON sessions
                BEGIN SELECT RAISE(ABORT, 'sources are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_sessions_delete BEFORE DELETE ON sessions
                BEGIN SELECT RAISE(ABORT, 'sources are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_turns BEFORE UPDATE ON turns
                BEGIN SELECT RAISE(ABORT, 'turns are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS preserve_turns_delete BEFORE DELETE ON turns
                BEGIN SELECT RAISE(ABORT, 'turns are immutable'); END;
        ''')

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def existing(self, raw, occurred_on):
        row = self.db.execute('SELECT * FROM sessions WHERE id=?', ('SES-' + digest(raw)[:16],)).fetchone()
        if row and row['occurred_on'] != occurred_on:
            raise ValueError('Same conversation already has a different date')
        return row is not None

    def records(self):
        rows = self.db.execute('SELECT o.*,s.occurred_on FROM observations o JOIN sessions s ON s.id=o.session_id ORDER BY s.occurred_on,s.rowid,o.rowid')
        result = []
        for row in rows:
            record = dict(row)
            record['observation'] = Observation.model_validate_json(record.pop('data'))
            record['vector'] = unblob(record['vector'])
            record['resolution'] = Resolution.model_validate_json(record['resolution'])
            result.append(record)
        return result

    def patterns(self):
        return {row['root_id']: dict(row) for row in self.db.execute('SELECT * FROM patterns ORDER BY id')}

    def sources(self):
        return [dict(row) for row in self.db.execute('SELECT s.*,a.data AS audit FROM sessions s JOIN analyses a ON a.session_id=s.id ORDER BY s.occurred_on,s.rowid')]

    def teaching_records(self):
        rows = self.db.execute('SELECT t.*,s.occurred_on FROM teaching_evidence t JOIN sessions s ON s.id=t.session_id ORDER BY s.occurred_on,t.rowid')
        return [{**dict(r), 'data': json.loads(r['data']), 'refs': json.loads(r['refs']), 'decision': json.loads(r['decision'])} for r in rows]

    def teaching_groups(self):
        evidence = self.teaching_records()
        return [{**dict(r), 'evidence': [e for e in evidence if e['directive_id'] == r['id']]} for r in self.db.execute('SELECT * FROM teaching_directives ORDER BY rowid')]

    def goals(self):
        return [{**dict(r), 'ref': json.loads(r['ref']) if r['ref'] else None} for r in self.db.execute('SELECT * FROM goals ORDER BY rowid')]

    def add_goal(self, text, session_id=None, ref=None):
        text = ' '.join(text.split())
        if not text or len(text) > 500:
            raise ValueError('Goal must contain 1-500 characters')
        gid = 'GOAL-' + digest(text.casefold())[:12]
        self.db.execute('INSERT OR IGNORE INTO goals VALUES (?,?,?,?)', (gid, text, session_id, json.dumps(ref) if ref else None))
        return gid

    def commit_session(self, raw, occurred_on, records, summaries, audit, policy, teaching=(), goals=()):
        date.fromisoformat(occurred_on)
        turns = parse(raw)
        if self.existing(raw, occurred_on):
            return
        sid = 'SES-' + digest(raw)[:16]
        previous = self.records()
        known = {r['id']: r for r in previous}
        prior_date = self.db.execute('SELECT MAX(occurred_on) FROM sessions').fetchone()[0]
        if prior_date and occurred_on < prior_date:
            raise ValueError('Ingest conversations chronologically; use reprocessing to rebuild earlier analyses')
        with self.db:
            self.db.execute('INSERT INTO sessions VALUES (?,?,?,?)', (sid, occurred_on, raw, hashlib.sha256(raw.encode('utf-8')).hexdigest()))
            self.db.executemany('INSERT INTO turns VALUES (?,?,?,?,?,?,?)', [(sid, t.number, t.speaker, t.start, t.end, t.line_start, t.line_end) for t in turns])
            self.db.execute('INSERT INTO analyses VALUES (?,?)', (sid, json.dumps(audit, ensure_ascii=False)))
            for record in records:
                o = record['observation']
                ref = reference(raw, turns, o.turn, o.source_excerpt, o.learner_quote, 'learner')
                if o.session_id != sid or any(getattr(o, k) != ref[k] for k in ('source_start', 'source_end', 'source_line_start', 'source_line_end')):
                    raise ValueError('Observation provenance/source mismatch')
                decision = record['resolution']
                if decision.candidate_id and decision.candidate_id not in known:
                    raise ValueError('Resolution refers to unknown evidence')
                expected_root = known[decision.candidate_id]['root_id'] if decision.decision == 'same_pattern' else o.id
                if record['root_id'] != expected_root:
                    raise ValueError('Invalid membership root')
                self.db.execute('INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)',
                    (o.id, sid, o.model_dump_json(), pedagogical_text(o), blob(record['vector']), record['embedding_model'], record['root_id'], decision.model_dump_json()))
                known[o.id] = record
            groups = {}
            for record in previous + records:
                groups.setdefault(record['root_id'], []).append(record)
            for root, members in groups.items():
                dates = {r['occurred_on'] for r in members if r['observation'].review.decision == 'keep'}
                if len(dates) >= policy.pattern_dates and root in summaries:
                    label, description, contexts = summaries[root]
                    self.db.execute('INSERT INTO patterns VALUES (?,?,?,?,?) ON CONFLICT(root_id) DO UPDATE SET label=excluded.label,description=excluded.description,contexts=excluded.contexts',
                        ('PAT-' + root.removeprefix('OBS-')[:12], root, label, description, json.dumps(contexts)))
            for item in teaching:
                did = item['directive_id']
                if did:
                    self.db.execute('INSERT OR IGNORE INTO teaching_directives VALUES (?,?)', (did, item['data']['instruction']))
                self.db.execute('INSERT INTO teaching_evidence VALUES (?,?,?,?,?,?)',
                    (item['id'], sid, json.dumps(item['data']), json.dumps(item['refs']), did, json.dumps(item['decision'])))
            for goal in goals:
                self.add_goal(goal['text'], sid, goal['ref'])

    def replace_analyses(self, rebuilt):
        """Publish a successful complete chronological replay, atomically; raw sources stay fixed."""
        if [(s['id'], s['source_sha256']) for s in self.sources()] != [(s['id'], s['source_sha256']) for s in rebuilt.sources()]:
            raise ValueError('Replay source set differs')
        tables = ['observations', 'patterns', 'teaching_evidence', 'teaching_directives', 'goals', 'analyses']
        with self.db:
            for table in tables:
                self.db.execute(f'DELETE FROM {table}')
            for table in ['analyses', 'patterns', 'observations', 'teaching_directives', 'teaching_evidence', 'goals']:
                rows = [tuple(r) for r in rebuilt.db.execute(f'SELECT * FROM {table}')]
                if rows:
                    marks = ','.join('?' for _ in rows[0])
                    self.db.executemany(f'INSERT INTO {table} VALUES ({marks})', rows)
