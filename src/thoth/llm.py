"""The logical LLM request is shared by manual ChatGPT and HTTP transports."""
from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError

from thoth.contracts import digest


def structured_payload(prompt: str, data: object, contract: type[BaseModel]) -> dict:
    schema = contract.model_json_schema()

    def strict(node):
        if isinstance(node, dict):
            if "properties" in node:
                node["required"] = list(node["properties"])
                node["additionalProperties"] = False
            for value in node.values():
                strict(value)
        elif isinstance(node, list):
            for value in node:
                strict(value)
    strict(schema)
    return {"messages": [{"role": "system", "content": prompt},
                         {"role": "user", "content": json.dumps(data, ensure_ascii=False)}],
            "response_format": {"type": "json_schema", "json_schema": {
                "name": contract.__name__, "strict": True, "schema": schema}}}


def render_payload(payload: dict) -> str:
    # Transport labels aren't model instructions. No gold, metrics, learner state,
    # or extractor reasoning is introduced by the manual adapter.
    parts = [f"=== {message['role'].upper()} ===\n{message['content']}"
             for message in payload["messages"]]
    parts.append("=== OUTPUT CONTRACT ===\nReturn only JSON conforming to this schema:\n" +
                 json.dumps(payload["response_format"]["json_schema"]["schema"], indent=2, ensure_ascii=False))
    return "\n\n".join(parts) + "\n"


def raw_digest(value: bytes) -> str:
    import hashlib
    return hashlib.sha256(value).hexdigest()


def parse_model_output(raw: str | bytes, contract: type[BaseModel], payload: dict):
    parsed = contract.model_validate_json(raw)
    # API strict-output schemas require explicit nulls/default-valued fields.
    # Enforce that same contract for manual output; Pydantic defaults alone would
    # otherwise silently accept omitted keys that the emitted schema requires.
    original = json.loads(raw)
    root = payload["response_format"]["json_schema"]["schema"]
    missing = []

    def check(value, node, location=()):
        if "$ref" in node:
            node = root["$defs"][node["$ref"].split("/")[-1]]
        if isinstance(value, dict):
            for key in node.get("required", []):
                if key not in value:
                    missing.append({"type": "missing", "loc": (*location, key), "input": value})
            for key, child in node.get("properties", {}).items():
                if key in value:
                    check(value[key], child, (*location, key))
        elif isinstance(value, list) and "items" in node:
            for index, item in enumerate(value):
                check(item, node["items"], (*location, index))
    check(original, root)
    if missing:
        raise ValidationError.from_exception_data(contract.__name__, missing)
    return parsed


class InvalidLLMResponse(ValueError):
    def __init__(self, stage: str, request_id: str, trace: dict):
        self.stage, self.request_id, self.trace = stage, request_id, trace
        super().__init__(f"Invalid {stage} model response for {request_id}; original response preserved")


class PendingLLMResponse(ValueError):
    """Transport has exported a request, but has no model response yet."""
