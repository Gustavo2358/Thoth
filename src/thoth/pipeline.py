from __future__ import annotations

import re

from thoth.adapters import Adapter
from thoth.contracts import (EXTRACTOR_VERSION, SCHEMA_VERSION, TAXONOMY_VERSION,
                             VERIFIER_VERSION, Observation, PipelineResult, Rejection,
                             canonical, digest)
from thoth.prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT
from thoth.provenance import validate
from thoth.llm import InvalidLLMResponse, PendingLLMResponse


def pipeline_metadata(adapter: Adapter) -> dict:
    # Implementation hash invalidates calibration after code changes, even if a
    # developer forgot to bump a human-readable version. Gold is deliberately excluded.
    from pathlib import Path
    modules = ("adapters.py", "text_adapter.py", "manual_adapter.py", "llm.py", "contracts.py", "pipeline.py", "provenance.py", "prompts.py", "evaluation.py", "benchmark.py")
    root = Path(__file__).parent
    m = {**adapter.metadata(), "schema_version": SCHEMA_VERSION,
         "taxonomy_version": TAXONOMY_VERSION, "extractor_prompt_version": EXTRACTOR_VERSION,
         "verifier_prompt_version": VERIFIER_VERSION,
         "extractor_prompt_hash": digest(EXTRACTION_PROMPT), "verifier_prompt_hash": digest(VERIFICATION_PROMPT),
         "implementation_hash": digest({n: (root / n).read_text() for n in modules})}
    return {**m, "pipeline_id": digest(m)}


def process(raw: str, session_id: str, adapter: Adapter) -> PipelineResult:
    metadata = pipeline_metadata(adapter)
    extraction, extract_trace = adapter.extract(raw)
    trace, accepted, rejected, seen = [extract_trace], [], [], {}
    pending, invalid = [], []
    for original in extraction.observations:
        p = original.model_copy(update={"construction": canonical(original.construction)})
        try:
            start, end = validate(raw, p.source_span, p.learner_utterance, p.corrected_form, p.teacher_comment)
        except ValueError as error:
            rejected.append(Rejection(proposal=p, reason="provenance: " + str(error)))
            continue
        literal_utterance = r"\s+".join(re.escape(t) for t in p.learner_utterance.split())
        utterance_matches = list(re.finditer(literal_utterance, raw[start:end]))
        if len(utterance_matches) != 1:
            rejected.append(Rejection(proposal=p, reason="provenance: learner quote occurs more than once in source span; narrow the span"))
            continue
        utterance_start = start + utterance_matches[0].start()
        utterance_end = start + utterance_matches[0].end()
        identity = (utterance_start, p.construction)
        signature = (p.outcome.value, p.production_mode.value, p.evidence_type.value, p.issue_kind, p.corrected_form)
        if identity in seen:
            previous, previous_signature = seen[identity]
            if previous_signature != signature:
                accepted[:] = [o for o in accepted if not (o.construction == p.construction and o.learner_utterance == p.learner_utterance and o.source_start <= utterance_start < o.source_end)]
                rejected.append(Rejection(proposal=previous, reason="conflicting proposals for one construction attempt"))
                rejected.append(Rejection(proposal=p, reason="conflicting proposals for one construction attempt"))
            else:
                rejected.append(Rejection(proposal=p, reason="duplicate observation"))
            continue
        seen[identity] = (p, signature)
        try:
            verdict, verify_trace = adapter.verify(p)
        except PendingLLMResponse as error:
            pending.append(error)
            continue
        except InvalidLLMResponse as error:
            invalid.append(error)
            continue
        trace.append(verify_trace)
        if verdict.decision == "unsupported":
            rejected.append(Rejection(proposal=p, reason="verifier: " + verdict.reason))
            continue
        # Unknown categories, style, opportunities, self repairs and unresolved
        # verification can be audited but cannot become successes/failures.
        quantitative = (verdict.decision == "supported" and p.construction != "unclassified"
                        and p.issue_kind in {"grammar", "none"}
                        and p.evidence_type.value not in {"opportunity", "self_correction", "other"})
        if not quantitative:
            p = type(p).model_validate({**p.model_dump(mode="json"), "outcome": "uncertain"})
        signals = {"provenance_valid": True, "classification_known": p.construction != "unclassified",
                   "independent_verifier_supported": verdict.decision == "supported",
                   "explicit_correction_present": p.evidence_type.value == "explicit_correction" and p.corrected_form is not None}
        observation = Observation.model_validate({
            **p.model_dump(mode="json"), "id": "OBS-" + digest([session_id, identity, signature, metadata["pipeline_id"]])[:20],
            "session_id": session_id, "source_start": start, "source_end": end,
            "learner_start": utterance_start, "learner_end": utterance_end,
            "pipeline_id": metadata["pipeline_id"], "verifier_decision": verdict.decision,
            "verifier_reason": verdict.reason, "support_signals": signals,
            "raw_support_score": sum(signals.values())})
        accepted.append(observation)
    if pending:
        raise PendingLLMResponse(f"{len(pending)} verifier responses pending; all required prompts exported")
    if invalid:
        raise invalid[0]
    return PipelineResult(observations=accepted, rejected=rejected, trace=trace, pipeline=metadata)
