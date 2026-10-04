from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(Strict):
    source_excerpt: str = Field(min_length=1)
    learner_quote: str = Field(min_length=1)
    production_mode: Literal["spontaneous", "prompted", "controlled", "unknown"]
    performance: Literal["successful", "difficulty", "uncertain"]
    evidence_type: Literal["observed_use", "correction", "self_correction", "opportunity"]
    communicative_intent: str = Field(min_length=1)
    learning_dimension: str = Field(min_length=1)
    observed_behavior: str = Field(min_length=1)
    suggested_forms: list[str]
    hypothesis: str | None

    @model_validator(mode="after")
    def special_evidence_is_uncertain(self):
        if self.evidence_type in {"opportunity", "self_correction"} and self.performance != "uncertain":
            raise ValueError("Opportunities and self-repairs are not independent successes or failures")
        return self


class Extraction(Strict):
    observations: list[Evidence]


class Review(Strict):
    decision: Literal["keep", "uncertain", "reject"]
    reason: str = Field(min_length=1)


class Observation(Evidence):
    id: str
    session_id: str
    source_start: int
    source_end: int
    review: Review


class Resolution(Strict):
    decision: Literal["same_pattern", "related_but_different", "new_pattern", "insufficient_evidence"]
    candidate_id: str | None
    reason: str = Field(min_length=1)
    pattern_label: str | None
    pattern_description: str | None
    conversation_contexts: list[str]

    @model_validator(mode="after")
    def consistent_decision(self):
        match = self.decision in {"same_pattern", "related_but_different"}
        if match != (self.candidate_id is not None):
            raise ValueError("Only same/related decisions identify a retrieved candidate")
        if self.decision == "same_pattern" and (not self.pattern_label or not self.pattern_description):
            raise ValueError("A same-pattern decision needs an evidence-grounded label and description")
        if self.decision != "same_pattern" and (self.pattern_label is not None or self.pattern_description is not None or self.conversation_contexts):
            raise ValueError("Unmatched/related evidence does not synthesize a pattern")
        return self


class Policy(Strict):
    neighbors: int = Field(ge=1, le=10)
    pattern_dates: int = Field(ge=2)
    practice_dates: int = Field(ge=2)
