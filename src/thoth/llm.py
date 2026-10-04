from __future__ import annotations

import json
import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel

from thoth.contracts import digest


class PendingResponse(RuntimeError):
    pass


def payload(prompt: str, data: dict, contract: type[BaseModel]) -> dict:
    return {"messages": [{"role": "system", "content": prompt},
                         {"role": "user", "content": json.dumps(data, ensure_ascii=False)}],
            "response_format": {"type": "json_schema", "json_schema": {
                "name": contract.__name__, "strict": True, "schema": contract.model_json_schema()}}}


def render(request: dict) -> str:
    return "\n\n".join("=== " + m["role"].upper() + " ===\n" + m["content"] for m in request["messages"]) + \
        "\n\n=== OUTPUT SCHEMA ===\n" + json.dumps(request["response_format"]["json_schema"]["schema"], indent=2) + "\n"


def immutable(path: Path, content: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"Refusing to overwrite original response/request: {path}")
    else:
        path.write_bytes(content)


class ManualChatGPTAdapter:
    def __init__(self, directory: Path, model: str, interactive=False):
        self.directory, self.model, self.interactive = Path(directory), model, interactive
        self.trace = []

    def metadata(self):
        return {"provider": "manual-chatgpt", "model": self.model,
                "identity": "operator declaration, not automatically verified"}

    def call(self, stage: str, prompt: str, data: dict, contract: type[BaseModel]):
        request = payload(prompt, data, contract)
        key = digest([self.metadata(), stage, request])
        case = self.directory / key
        immutable(case / "request.json", json.dumps({"stage": stage, "model": self.metadata(),
                  "payload": request}, indent=2, ensure_ascii=False).encode())
        immutable(case / "request.txt", render(request).encode())
        response = case / "response.txt"
        if not response.exists() and self.interactive:
            print(f"=== {stage} / {key} ===\n" + render(request))
            print("Paste original JSON. Finish with END_JSON or EOF.")
            lines = []
            for line in sys.stdin:
                if line.strip() == "END_JSON":
                    break
                lines.append(line)
            if lines:
                immutable(response, "".join(lines).encode())
        if not response.exists():
            raise PendingResponse(f"Fill {response}; prompt: {case / 'request.txt'}")
        raw = response.read_bytes()
        response_hash = hashlib.sha256(raw).hexdigest()
        immutable(case / "response.sha256", response_hash.encode())
        try:
            parsed = contract.model_validate_json(raw)
        except ValueError:
            (case / "validation.txt").write_text("INVALID; original response preserved\n")
            raise
        immutable(case / "parsed.json", parsed.model_dump_json(indent=2).encode())
        self.trace.append({"stage": stage, "request": key, "response_hash": response_hash, "model": self.model})
        return parsed

    def import_responses(self, source: Path):
        files = sorted(source.glob("*.txt"))
        if not files:
            raise ValueError("No response .txt files; filenames must be <request-hash>.txt")
        for file in files:
            if not (self.directory / file.stem / "request.json").exists():
                raise ValueError(f"Unknown request: {file.stem}")
            existing = self.directory / file.stem / "response.txt"
            if existing.exists() and existing.read_bytes() != file.read_bytes():
                raise ValueError("Keep original answers; use a separate exchange to retry")
        for file in files:
            raw = file.read_bytes()
            immutable(self.directory / file.stem / "response.txt", raw)
            immutable(self.directory / file.stem / "response.sha256", hashlib.sha256(raw).hexdigest().encode())
        return len(files)


class OpenAIAdapter:
    def __init__(self, model: str):
        if not model or model.startswith("ChatGPT /"):
            raise ValueError("Specify an API model explicitly with --model")
        self.model = model
        self.key = os.environ.get("OPENAI_API_KEY")
        if not self.key:
            raise ValueError("Configure OPENAI_API_KEY securely")
        self.base = os.environ.get("THOTH_API_BASE", "https://api.openai.com/v1").rstrip("/")
        url = urlsplit(self.base)
        if url.scheme != "https" or url.username or url.password or url.query or url.fragment:
            raise ValueError("API base must be a credential-free HTTPS URL")
        self.trace = []

    def metadata(self):
        return {"provider": "openai", "model": self.model, "endpoint": self.base}

    def call(self, stage, prompt, data, contract):
        request = {"model": self.model, "temperature": 0, **payload(prompt, data, contract)}
        with httpx.Client(timeout=120) as client:
            response = client.post(self.base + "/chat/completions", json=request,
                                   headers={"Authorization": "Bearer " + self.key})
        if response.is_error:
            raise RuntimeError(f"LLM HTTP {response.status_code}")
        choice = response.json()["choices"][0]
        if choice.get("finish_reason") != "stop" or choice["message"].get("refusal"):
            raise RuntimeError("Model refused or truncated output")
        raw = choice["message"]["content"]
        parsed = contract.model_validate_json(raw)
        self.trace.append({"stage": stage, "model": self.model, "request": request, "response": raw})
        return parsed
