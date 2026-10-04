from __future__ import annotations

import json
import os
import re
from typing import Protocol, TypeVar
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel

from thoth.contracts import Extraction, Proposal, TAXONOMY, Verdict, digest
from thoth.prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT
from thoth.llm import parse_model_output, structured_payload

T = TypeVar("T", bound=BaseModel)


class LLMPort(Protocol):
    def metadata(self) -> dict: ...
    def extract(self, raw: str) -> tuple[Extraction, dict]: ...
    def verify(self, proposal: Proposal) -> tuple[Verdict, dict]: ...


Adapter = LLMPort  # Backwards-compatible name for the domain port.


class OpenAIAdapter:
    """Thin OpenAI-compatible structured-output adapter; no agent framework."""

    def __init__(self, model: str | None = None, verifier_model: str | None = None):
        self.key = os.environ.get("THOTH_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not self.key:
            raise ValueError("LLM credential missing: configure THOTH_API_KEY securely")
        self.base = os.environ.get("THOTH_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        url = urlsplit(self.base)
        if url.username or url.password or url.query or url.fragment:
            raise ValueError("base URL must not contain credentials, query or fragment")
        if url.scheme != "https" and not (url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1"}):
            raise ValueError("LLM endpoint must use HTTPS (except local development)")
        self.model = model or os.environ.get("THOTH_MODEL", "gpt-4.1-mini")
        self.verifier_model = verifier_model or os.environ.get("THOTH_VERIFIER_MODEL", self.model)

    def metadata(self) -> dict:
        return {"provider": "openai-compatible", "endpoint": self.base,
                "model": self.model, "verifier_model": self.verifier_model,
                "temperature": 0, "adapter_version": "openai-1"}

    def _call(self, model: str, prompt: str, data: object, contract: type[T]) -> tuple[T, dict]:
        request = {"model": model, "temperature": 0, **structured_payload(prompt, data, contract)}
        with httpx.Client(timeout=120, follow_redirects=False) as client:
            response = client.post(self.base + "/chat/completions", json=request,
                                   headers={"Authorization": "Bearer " + self.key})
        if response.is_error:
            # Don't log response bodies: some gateways echo credentials.
            raise RuntimeError(f"LLM HTTP {response.status_code}; no run activated")
        body = response.json()
        choice = body["choices"][0]
        if choice.get("finish_reason") != "stop" or choice["message"].get("refusal"):
            raise RuntimeError("LLM refused or truncated output; no run activated")
        content = choice["message"]["content"]
        parsed = parse_model_output(content, contract, request)
        trace = {"stage": contract.__name__, "model": model, "response": parsed.model_dump(mode="json"),
                 "raw_response": content,
                 "usage": body.get("usage"), "system_fingerprint": body.get("system_fingerprint")}
        return parsed, trace

    def extract(self, raw: str) -> tuple[Extraction, dict]:
        return self._call(self.model, EXTRACTION_PROMPT.format(taxonomy=", ".join(TAXONOMY)),
                          {"document": raw}, Extraction)

    def verify(self, proposal: Proposal) -> tuple[Verdict, dict]:
        return self._call(self.verifier_model, VERIFICATION_PROMPT,
                          {"excerpt": proposal.source_span, "proposal": proposal.model_dump(mode="json")}, Verdict)


LEARNER = re.compile(
    r'(?:learner|student|he|she)\s+(?:said|answered|responded)(?:\s+spontaneously)?\s*:\s*["“]([^"”]+)["”]', re.I)
CORRECTION = re.compile(r'(?:corrected (?:this )?to|correction|suggested instead|reviewed the form)\s*:\s*["“]([^"”]+)["”]', re.I)


def mode_of(text: str) -> str:
    lower = text.lower()
    if "controlled" in lower or "drill" in lower:
        return "controlled"
    if "prompted" in lower or "elicited" in lower:
        return "prompted"
    if "spontaneous" in lower or "spontaneously" in lower:
        return "spontaneous"
    return "unknown"


def families(utterance: str, context: str) -> list[str]:
    """Candidate discovery, deliberately limited to a documented report dialect."""
    u = utterance.lower().replace("’", "'")
    result = []
    if "since" in u or re.search(r"for (?:\d+|one|two|three|four|five) (?:years?|months?|days?|weeks?)", u):
        result.append("present_perfect.vs_simple_past" if "ended job" in context.lower()
                      else "present_perfect.continuous" if re.search(r"(?:been|have|has) \w+ing", u)
                      else "present_perfect.duration")
    if re.search(r"since (?:\d+|one|two|three|four|five) (?:years?|months?|days?|weeks?)|for (?:20\d\d|january|monday)", u):
        result.append("duration.since_for")
    if "yesterday" in u or "last year" in u:
        result.append("present_perfect.vs_simple_past")
    if re.match(r"(?:where|what|when|why|how) ", u) and "?" in u:
        result.append("question.do_support")
    if "should" in u and re.search(r"(?:told|tell|sent|send|done|went|gone)", u):
        result.append("modal_perfect.should_have")
    if re.search(r"\b(?:a|an) (?:engineer|developer|information|advice|apple|university)", u):
        result.append("article.indefinite")
    if re.search(r"\b(?:did (?:not )?went|does (?:not )?works|will (?:not )?can|will (?:not )?be working|did (?:not )?(?:you )?go)\b", u):
        result.append("auxiliary.chain")
    return result


class OfflineAdapter:
    """Conservative rule baseline, NOT a substitute for real-model qualification.

    Reads narrative blocks with attributed learner quotes, not gold labels. Gold is
    independently authored. Rules know only eight narrow construction families.
    """

    def metadata(self) -> dict:
        return {"provider": "offline-rules", "model": "narrative-baseline-1",
                "verifier_model": "independent-grammar-checks-1", "adapter_version": "offline-1"}

    def extract(self, raw: str) -> tuple[Extraction, dict]:
        proposals = []
        for block in re.split(r"\n\s*\n", raw):
            for match in LEARNER.finditer(block):
                u = match.group(1)
                # One learner per narrative block is the offline baseline's supported dialect.
                if len(list(LEARNER.finditer(block))) > 1:
                    continue
                correction_match = CORRECTION.search(block)
                correction = correction_match.group(1) if correction_match else None
                lower = block.lower()
                style = "more natural" in lower or "stylistic" in lower or "vocabulary suggestion" in lower
                opportunity = "opportunity" in lower or "target was not selected" in lower
                self_corrected = "sorry" in u.lower()
                targets = families(u, block)
                if opportunity:
                    targets = ["present_perfect.duration"]
                if style:
                    targets = ["unclassified"]
                if not targets and "insufficient context" in lower:
                    targets = ["unclassified"]
                for family in targets:
                    uncertain = style or opportunity or self_corrected or "insufficient context" in lower
                    outcome = "uncertain" if uncertain else "incorrect" if correction else "correct"
                    # Local success can coexist with a repair to another construction.
                    # Teacher disagreement triggers conservative abstention rather than
                    # treating the teacher as ground truth. Independent verifier decides.
                    if "tense is valid" in lower and family == "present_perfect.duration":
                        outcome = "correct"
                    evidence = "opportunity" if opportunity else "self_correction" if self_corrected else (
                        "other" if style or uncertain else "explicit_correction" if correction and outcome == "incorrect" else "successful_use")
                    proposals.append(Proposal(
                        source_span=block.strip(), learner_utterance=u, corrected_form=correction if outcome == "incorrect" else None,
                        construction=family, outcome=outcome, production_mode=mode_of(block),
                        evidence_type=evidence, issue_kind="vocabulary" if "vocabulary suggestion" in lower else "style" if style else "unclear" if uncertain else "grammar" if outcome == "incorrect" else "none",
                        feature="question" if u.strip().endswith("?") else "negative" if re.search(r"\bnot\b|n't", u) else "affirmative"))
        result = Extraction(observations=proposals)
        return result, {"stage": "Extraction", "response": result.model_dump(mode="json")}

    def verify(self, proposal: Proposal) -> tuple[Verdict, dict]:
        verdict = offline_verdict(proposal)
        return verdict, {"stage": "Verdict", "response": verdict.model_dump(mode="json")}


def grammar_status(u: str, family: str, context: str) -> str:
    """Independent verifier predicates: grammatical, erroneous, or unresolved.

    Intentionally do not call candidate discovery or rely on teacher approval.
    Limited forms must abstain outside coverage.
    """
    u = u.lower().replace("’", "'")
    context = context.lower()
    perfect = bool(re.search(r"\b(?:have|has|i've|he's|she's|we've|they've) (?:not )?(?:lived|worked|been|visited|finished)", u))
    if family == "present_perfect.duration":
        if "ended job" in context or "no longer" in context:
            return "correct" if re.search(r"\b(?:worked|lived)\b", u) and not perfect else "uncertain"
        if "since" not in u and "for" not in u:
            return "uncertain"
        if perfect:
            return "correct"
        if "still" in context or "continues" in context or "since 20" in u:
            return "incorrect" if re.search(r"\bi (?:live|work|worked|lived)\b", u) else "uncertain"
    elif family == "present_perfect.vs_simple_past":
        if "ended job" in context and re.search(r"\b(?:worked|lived)\b", u) and not perfect:
            return "correct"
        if "yesterday" in u or "last year" in u:
            return "incorrect" if perfect else "correct" if re.search(r"\b(?:visited|finished|worked)\b", u) else "uncertain"
    elif family == "present_perfect.continuous":
        if re.search(r"(?:have|has|i've|we've) (?:not )?been \w+ing", u):
            return "correct"
        if re.search(r"(?:have|has|i've) (?:not )?\w+ing", u):
            return "incorrect"
    elif family == "duration.since_for":
        if re.search(r"since \w+ (?:years?|months?|days?|weeks?)|for (?:20\d\d|january|monday)", u):
            return "incorrect"
        if re.search(r"since (?:20\d\d|january|monday)|for \w+ (?:years?|months?|days?|weeks?)", u):
            return "correct"
    elif family == "question.do_support":
        if re.match(r"(?:where|what|when|why|how) (?:do|does|did) \w+ (?:work|live|go|like)\b", u):
            return "correct"
        if re.match(r"(?:where|what|when|why|how) (?:you|he|she) (?:work|live|go|like)\b", u):
            return "incorrect"
    elif family == "modal_perfect.should_have":
        if re.search(r"should (?:not )?have (?:told|sent|done|gone)", u):
            return "correct"
        if re.search(r"should (?:not )?(?:told|sent|done|went)", u):
            return "incorrect"
    elif family == "article.indefinite":
        if re.search(r"\b(?:a (?:engineer|information|advice|apple)|an (?:developer|university))\b", u):
            return "incorrect"
        if re.search(r"\b(?:an (?:engineer|apple)|a (?:developer|university))\b", u):
            return "correct"
        if re.search(r"\b(?:the|some) (?:information|advice)\b", u):
            return "correct"
    elif family == "auxiliary.chain":
        if re.search(r"\b(?:did (?:not )?went|does (?:not )?works|will (?:not )?can)\b", u):
            return "incorrect"
        if re.search(r"\b(?:did (?:not )?(?:you )?go|will (?:not )?be working)\b", u):
            return "correct"
    return "uncertain"


def offline_verdict(p: Proposal) -> Verdict:
    attributions = [m.group(1) for m in LEARNER.finditer(p.source_span)]
    if p.learner_utterance not in attributions:
        return Verdict(decision="unsupported", reason="No exact attributed learner quote in this report dialect")
    if p.production_mode.value != mode_of(p.source_span):
        return Verdict(decision="unsupported", reason="Production mode lacks contextual support")
    if p.evidence_type.value in {"opportunity", "self_correction"}:
        return Verdict(decision="supported" if p.outcome.value == "uncertain" else "unsupported",
                       reason="Non-independent attempt; retain separately without accuracy counting")
    if p.issue_kind in {"style", "vocabulary", "unclear"}:
        return Verdict(decision="uncertain", reason="No supported grammatical outcome")
    actual = grammar_status(p.learner_utterance, p.construction, p.source_span)
    if actual == "uncertain":
        return Verdict(decision="uncertain", reason="Verifier predicates do not resolve this context")
    if actual != p.outcome.value:
        return Verdict(decision="unsupported", reason="Independent grammatical check contradicts the proposed outcome")
    if p.corrected_form and grammar_status(p.corrected_form, p.construction, p.source_span) != "correct":
        return Verdict(decision="uncertain", reason="Teacher correction is not independently supported")
    return Verdict(decision="supported", reason="Independent grammatical predicate and source agree")


def adapter(name: str, model: str | None = None, verifier_model: str | None = None,
            responses_dir=None, interactive: bool = False, export_directory=None,
            evaluation_design: str = "unverified") -> LLMPort:
    if name == "manual":
        from pathlib import Path
        from thoth.manual_adapter import ManualChatGPTAdapter
        return ManualChatGPTAdapter(Path(responses_dir or "data/manual-chat"), model,
                                    verifier_model, interactive, export_directory, evaluation_design)
    if name == "text":
        from pathlib import Path
        from thoth.text_adapter import TextAdapter
        return TextAdapter(Path(responses_dir or "benchmark/text-exchange"), model or "codex-session", interactive)
    return OfflineAdapter() if name == "offline" else OpenAIAdapter(model, verifier_model)
