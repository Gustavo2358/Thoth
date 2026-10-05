"""The sole import boundary: role-labelled Markdown, never speaker guessing."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re

from thoth.provenance import locate


@dataclass(frozen=True)
class Turn:
    number: int
    speaker: str
    start: int
    end: int
    line_start: int
    line_end: int
    text: str


def parse(raw: str) -> list[Turn]:
    roles = {"user": "learner", "learner": "learner", "assistant": "teacher", "teacher": "teacher"}
    headers, offset, fence = [], 0, None
    for line in raw.splitlines(keepends=True):
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
        elif marker:
            fence = marker[1]
        else:
            heading = re.fullmatch(r"##\s+(.+?)\s*", stripped)
            if heading:
                label = heading[1].casefold()
                if label not in roles:
                    raise ValueError(f"Unknown speaker heading at line {raw[:offset].count(chr(10)) + 1}: {heading[1]}")
                headers.append((offset, offset + len(line), roles[label]))
        offset += len(line)
    if fence:
        raise ValueError("Unclosed Markdown fence; speaker boundaries are ambiguous")
    if not headers or {h[2] for h in headers} != {"learner", "teacher"}:
        raise ValueError("Expected role-labelled Markdown with ## User / ## Assistant (or Learner / Teacher)")
    preamble = raw[:headers[0][0]]
    if any(line.strip() and not re.fullmatch(r"#\s+[^#].*", line) for line in preamble.splitlines()):
        raise ValueError("Unlabelled content before the first turn; only a title is allowed")
    turns = []
    for i, (_, start, speaker) in enumerate(headers):
        end = headers[i + 1][0] if i + 1 < len(headers) else len(raw)
        if not raw[start:end].strip():
            raise ValueError(f"Empty turn {i + 1}")
        turns.append(Turn(i + 1, speaker, start, end, raw[:start].count("\n") + 1,
                          raw[:end].count("\n") + (not raw[:end].endswith("\n")), raw[start:end]))
    return turns


def reference(raw, turns, number, excerpt, quote=None, speaker=None):
    if not 1 <= number <= len(turns):
        raise ValueError("Evidence refers to an unknown turn")
    turn = turns[number - 1]
    if speaker and turn.speaker != speaker:
        raise ValueError(f"Evidence must be attributed to {speaker}, not {turn.speaker}")
    start, end = locate(turn.text, excerpt, quote or excerpt)
    start, end = start + turn.start, end + turn.start
    return dict(turn=number, speaker=turn.speaker, quote=quote or excerpt,
                source_start=start, source_end=end,
                source_line_start=raw[:start].count("\n") + 1,
                source_line_end=raw[:end].count("\n") + 1)


def context(turns):
    return [asdict(t) for t in turns]
