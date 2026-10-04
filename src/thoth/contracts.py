from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "observation-1"
TAXONOMY_VERSION = "taxonomy-1"
EXTRACTOR_VERSION = "extractor-1"
VERIFIER_VERSION = "verifier-1"

TAXONOMY = {
    "present_perfect.duration": "Present perfect — duration",
    "present_perfect.vs_simple_past": "Present perfect vs. simple past",
    "present_perfect.continuous": "Present perfect continuous",
    "duration.since_for": "Since vs. for",
    "question.do_support": "Question formation — do support",
    "modal_perfect.should_have": "Modal perfect — should have",
    "article.indefinite": "Indefinite articles",
    "auxiliary.chain": "Auxiliary chains",
    "unclassified": "Unclassified",
}
ALIASES = {
    "present_perfect_duration": "present_perfect.duration",
    "since_vs_for": "duration.since_for",
    "question_formation": "question.do_support",
    "modal_perfect": "modal_perfect.should_have",
    "articles": "article.indefinite",
    "unknown": "unclassified",
}


def canonical(value: str) -> str:
    return value if value in TAXONOMY else ALIASES.get(value, "unclassified")


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Outcome(str, Enum):
    correct = "correct"
    incorrect = "incorrect"
    uncertain = "uncertain"


class Mode(str, Enum):
    spontaneous = "spontaneous"
    prompted = "prompted"
    controlled = "controlled"
    unknown = "unknown"


class Evidence(str, Enum):
    successful_use = "successful_use"
    explicit_correction = "explicit_correction"
    inferred_error = "inferred_error"
    opportunity = "opportunity"
    self_correction = "self_correction"
    other = "other"


class Proposal(StrictModel):
    source_span: str = Field(min_length=1)
    learner_utterance: str = Field(min_length=1)
    corrected_form: str | None = None
    teacher_comment: str | None = None
    construction: str
    feature: Literal["affirmative", "negative", "question", "unknown"] = "unknown"
    outcome: Outcome
    production_mode: Mode
    evidence_type: Evidence
    issue_kind: Literal["grammar", "style", "vocabulary", "unclear", "none"]


class Extraction(StrictModel):
    observations: list[Proposal]


class Verdict(StrictModel):
    decision: Literal["supported", "unsupported", "uncertain"]
    reason: str


class Observation(Proposal):
    id: str
    session_id: str
    source_start: int = Field(ge=0)
    source_end: int = Field(gt=0)
    learner_start: int = Field(ge=0)
    learner_end: int = Field(gt=0)
    schema_version: str = SCHEMA_VERSION
    extractor_version: str = EXTRACTOR_VERSION
    verifier_version: str = VERIFIER_VERSION
    pipeline_id: str
    verifier_decision: Literal["supported", "uncertain"]
    verifier_reason: str
    provenance_valid: Literal[True] = True
    support_signals: dict[str, bool]
    raw_support_score: int = Field(ge=1, le=4)


class Rejection(StrictModel):
    proposal: Proposal
    reason: str


class PipelineResult(StrictModel):
    observations: list[Observation]
    rejected: list[Rejection]
    trace: list[dict]
    pipeline: dict
