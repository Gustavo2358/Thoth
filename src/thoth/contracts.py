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
    turn: int = Field(ge=1)
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
    support: Literal["no_support", "contextual_prompt", "partial_scaffold", "explanation_before_attempt", "model_phrase_available", "immediate_repetition", "unknown"]
    support_turns: list[int]

    @model_validator(mode="after")
    def support_and_mode(self):
        if self.support in {"immediate_repetition", "model_phrase_available"} and self.production_mode != "controlled":
            raise ValueError("A supplied model is controlled production")
        if self.production_mode == "spontaneous" and self.support != "no_support":
            raise ValueError("Spontaneous production requires no support")
        if self.support in {"partial_scaffold", "explanation_before_attempt", "contextual_prompt"} and self.production_mode not in {"prompted", "controlled"}:
            raise ValueError("Scaffolded production is prompted or controlled")
        if self.support in {"no_support", "unknown"} and self.support_turns:
            raise ValueError("No support/unknown cannot identify supplied support")
        if self.support not in {"no_support", "unknown"} and not self.support_turns:
            raise ValueError("Identify the earlier teacher turns providing support")
        if any(t >= self.turn or t < 1 for t in self.support_turns):
            raise ValueError("Support must precede the attempt")
        return self

    @model_validator(mode="after")
    def special_evidence_is_uncertain(self):
        if self.evidence_type in {"opportunity", "self_correction"} and self.performance != "uncertain":
            raise ValueError("Opportunities and self-repairs are not independent successes or failures")
        return self


class SourceRef(Strict):
    turn: int = Field(ge=1)
    quote: str = Field(min_length=1)


class TeachingEvidence(Strict):
    refs: list[SourceRef] = Field(min_length=1)
    kind: Literal["explicit_preference", "situational_request", "intervention_response", "rejection"]
    interpretation: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    durable: bool

    @model_validator(mode="after")
    def durable_request(self):
        if self.durable and self.kind not in {"explicit_preference", "rejection"}:
            raise ValueError("A local request or reaction is not a durable preference")
        return self


class GoalEvidence(Strict):
    ref: SourceRef
    text: str = Field(min_length=1, max_length=500)


class Extraction(Strict):
    observations: list[Evidence]
    teaching: list[TeachingEvidence]
    goals: list[GoalEvidence]


class Review(Strict):
    decision: Literal["keep", "uncertain", "reject"]
    reason: str = Field(min_length=1)


class Observation(Evidence):
    id: str
    session_id: str
    source_start: int
    source_end: int
    review: Review
    source_line_start: int
    source_line_end: int


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
    recovery_dates: int = Field(default=1, ge=1)
    stale_dates: int = Field(default=3, ge=1)
    stale_days: int = Field(default=30, ge=1)
    prompt_chars: int = Field(default=8000, ge=4000)
    practice_limit: int = Field(default=2, ge=0, le=3)
    observe_limit: int = Field(default=2, ge=0, le=3)
    transfer_limit: int = Field(default=2, ge=0, le=3)


class TeachingDecision(Strict):
    decision: Literal["same_directive", "new_directive", "evidence_only", "reject"]
    directive_id: str | None
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def membership(self):
        if (self.decision == "same_directive") != (self.directive_id is not None):
            raise ValueError("Only same_directive identifies an existing directive")
        return self
