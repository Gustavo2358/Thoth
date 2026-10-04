"""Operator-mediated LLM adapter: schema prompts out, JSON responses in.

No gold or learner state is made available to the operator through this adapter.
Export/replay makes a chat-assisted evaluation inspectable without an API key.
It does not turn that evaluation into an independently blinded experiment.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from thoth.artifacts import write_json
from thoth.contracts import Extraction, Proposal, TAXONOMY, Verdict, canonical, digest
from thoth.prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT
from thoth.llm import PendingLLMResponse


class PendingResponse(PendingLLMResponse):
    pass


class TextAdapter:
    def __init__(self, directory: Path, model: str = "codex-session", interactive: bool = False):
        self.directory = directory
        self.model = model
        self.interactive = interactive

    def metadata(self) -> dict:
        return {"provider": "text-input", "model": self.model, "verifier_model": self.model,
                "adapter_version": "text-1", "evaluation_kind": "operator-mediated, not independent blind API evaluation"}

    def request(self, stage: str, data: dict, contract, prompt: str) -> tuple[dict, Path]:
        request = {"stage": stage, "pipeline_adapter": self.metadata(), "system_prompt": prompt,
                   "user_input": data, "response_schema": contract.model_json_schema()}
        key = digest(request)
        request["request_sha256"] = key
        path = self.directory / "requests" / (key + ".json")
        if path.exists() and json.loads(path.read_text()) != request:
            raise ValueError("Conflicting immutable prompt record")
        write_json(path, request)
        return request, self.directory / "responses" / (key + ".json")

    def _call(self, stage: str, data: dict, contract, prompt: str):
        request, response_path = self.request(stage, data, contract, prompt)
        if not response_path.exists() and self.interactive:
            print(json.dumps(request, indent=2, ensure_ascii=False))
            print("Paste response JSON. Finish with a line containing only END_JSON.")
            lines = []
            for line in sys.stdin:
                if line.strip() == "END_JSON":
                    break
                lines.append(line)
            else:
                raise PendingResponse("Input ended before END_JSON; response not saved")
            parsed = contract.model_validate_json("".join(lines))
            write_json(response_path, {"request_sha256": request["request_sha256"],
                                       "submitted_by": "interactive-operator",
                                       "response": parsed.model_dump(mode="json")})
        if not response_path.exists():
            raise PendingResponse(f"Response pending for {stage}. Prompt: {self.directory / 'requests' / (request['request_sha256'] + '.json')}; put response envelope at {response_path}")
        envelope = json.loads(response_path.read_text())
        if envelope["request_sha256"] != request["request_sha256"]:
            raise ValueError("Response does not belong to this prompt")
        parsed = contract.model_validate(envelope["response"])
        return parsed, {"stage": contract.__name__, "request_sha256": request["request_sha256"],
                        "response_sha256": digest(envelope), "submitted_by": envelope.get("submitted_by", "unspecified"),
                        "response": parsed.model_dump(mode="json")}

    def extraction_request(self, raw: str):
        return self.request("Extraction", {"document": raw}, Extraction,
                            EXTRACTION_PROMPT.format(taxonomy=", ".join(TAXONOMY)))

    def export_requests(self, raw: str) -> int:
        request, response_path = self.extraction_request(raw)
        if not response_path.exists():
            return 1
        extraction, _ = self.extract(raw)
        pending = 0
        for original in extraction.observations:
            p = original.model_copy(update={"construction": canonical(original.construction)})
            _, response_path = self.request("Verdict", {"excerpt": p.source_span, "proposal": p.model_dump(mode="json")}, Verdict, VERIFICATION_PROMPT)
            pending += not response_path.exists()
        return pending

    def extract(self, raw: str):
        return self._call("Extraction", {"document": raw}, Extraction,
                          EXTRACTION_PROMPT.format(taxonomy=", ".join(TAXONOMY)))

    def verify(self, proposal: Proposal):
        return self._call("Verdict", {"excerpt": proposal.source_span,
                                      "proposal": proposal.model_dump(mode="json")}, Verdict, VERIFICATION_PROMPT)
