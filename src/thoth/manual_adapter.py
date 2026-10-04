"""First-class subscription ChatGPT runtime, with immutable raw responses."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from thoth.artifacts import write_json
from thoth.contracts import (EXTRACTOR_VERSION, SCHEMA_VERSION, TAXONOMY, VERIFIER_VERSION,
                             Extraction, Proposal, Verdict, digest)
from thoth.llm import InvalidLLMResponse, parse_model_output, raw_digest, render_payload, structured_payload
from thoth.prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT
from thoth.text_adapter import PendingResponse


class ManualChatGPTAdapter:
    def __init__(self, directory: Path, model: str | None = None,
                 verifier_model: str | None = None, interactive: bool = False,
                 export_directory: Path | None = None, evaluation_design: str = "unverified"):
        self.directory = Path(directory)
        self.model = model or "ChatGPT / unspecified"
        self.verifier_model = verifier_model or self.model
        self.interactive = interactive
        self.export_directory = export_directory
        self.evaluation_design = evaluation_design
        self.interactions: list[dict] = []

    def metadata(self) -> dict:
        return {"provider": "manual-chatgpt", "mode": "manual-chat", "model": self.model,
                "verifier_model": self.verifier_model, "adapter_version": "manual-1",
                "model_identity_source": "operator-declared label; not automatically verified",
                "evaluation_design": self.evaluation_design}

    def _manifest(self) -> dict:
        path = self.directory / "exchange.json"
        if path.exists():
            saved = json.loads(path.read_bytes())
            if saved["metadata"] != self.metadata():
                raise ValueError("Manual exchange belongs to a different model/configuration; use a separate directory")
            return saved
        return {"metadata": self.metadata(), "requests": []}

    def request(self, stage: str, data: dict, contract, prompt: str) -> tuple[dict, Path]:
        payload = structured_payload(prompt, data, contract)
        request_id = digest({"payload": payload, "adapter": self.metadata()})
        request = {"request_sha256": request_id, "logical_payload_sha256": digest(payload),
                   "stage": stage, "metadata": {**self.metadata(), "schema_version": SCHEMA_VERSION,
                   "extractor_prompt_version": EXTRACTOR_VERSION, "verifier_prompt_version": VERIFIER_VERSION},
                   "logical_payload": payload}
        manifest = self._manifest()
        entry = next((e for e in manifest["requests"] if e["request_sha256"] == request_id), None)
        if entry is None:
            number = len(manifest["requests"]) + 1
            entry = {"request_sha256": request_id, "stage": stage,
                     "filename": f"{number:03d}-{'extractor' if stage == 'Extraction' else 'verifier'}.txt"}
            manifest["requests"].append(entry)
        case = self.directory / "cases" / request_id
        case.mkdir(parents=True, exist_ok=True)
        path = case / "request.json"
        if path.exists() and json.loads(path.read_bytes()) != request:
            raise ValueError("Conflicting immutable manual request")
        write_json(path, request)
        rendered = render_payload(payload).encode("utf-8")
        self._immutable_bytes(case / "request.txt", rendered)
        write_json(self.directory / "exchange.json", manifest)
        if self.export_directory is not None:
            self.export_directory.mkdir(parents=True, exist_ok=True)
            self._immutable_bytes(self.export_directory / entry["filename"], rendered)
            # Identifies response filenames and logical hashes; contains no labels.
            write_json(self.export_directory / "manifest.json", manifest)
        return request, case

    @staticmethod
    def _immutable_bytes(path: Path, content: bytes):
        if path.exists():
            if path.read_bytes() != content:
                raise ValueError(f"Refusing to replace original interaction: {path}")
            return
        with path.open("xb") as file:
            file.write(content)

    def _capture(self, case: Path, request_id: str, raw: bytes):
        self._immutable_bytes(case / "response.txt", raw)
        record = {"request_sha256": request_id, "response_sha256": raw_digest(raw)}
        path = case / "capture.json"
        if path.exists() and json.loads(path.read_bytes()) != record:
            raise ValueError("Original manual response integrity check failed")
        write_json(path, record)

    def _parse(self, request: dict, case: Path, contract):
        raw = (case / "response.txt").read_bytes()
        capture = json.loads((case / "capture.json").read_bytes())
        if capture != {"request_sha256": request["request_sha256"], "response_sha256": raw_digest(raw)}:
            raise ValueError("Original manual response was modified; do not repair benchmark responses")
        trace = {"stage": request["stage"], "request_sha256": request["request_sha256"],
                 "response_sha256": raw_digest(raw), "case_directory": str(case),
                 "mode": "manual-chat", "submitted_by": "operator", "status": "invalid"}
        try:
            # No fence removal, repair, coercion of prose, or rewriting of the raw.
            parsed = parse_model_output(raw, contract, request["logical_payload"])
        except ValidationError as error:
            validation = {"status": "invalid", "errors": error.errors(include_url=False, include_input=False),
                          "response_sha256": raw_digest(raw)}
            write_json(case / "validation.json", validation)
            trace["validation_errors"] = validation["errors"]
            self.interactions.append(trace)
            raise InvalidLLMResponse(request["stage"], request["request_sha256"], trace) from error
        trace.update(status="valid", response=parsed.model_dump(mode="json"))
        write_json(case / "parsed.json", parsed.model_dump(mode="json"))
        write_json(case / "validation.json", {"status": "valid", "response_sha256": raw_digest(raw)})
        self.interactions.append(trace)
        return parsed, trace

    def import_responses(self, directory: Path) -> dict:
        manifest = self._manifest()
        entries = {e["filename"]: e for e in manifest["requests"]}
        entries.update({e["request_sha256"] + ".txt": e for e in manifest["requests"]})
        sources = sorted(Path(directory).glob("*.txt"))
        if not sources:
            raise ValueError("No .txt response files found")
        planned = []
        for source in sources:
            if source.name not in entries:
                raise ValueError(f"Unknown response filename {source.name}; use the exported manifest")
            entry = entries[source.name]
            case = self.directory / "cases" / entry["request_sha256"]
            raw = source.read_bytes()
            if (case / "response.txt").exists() and (case / "response.txt").read_bytes() != raw:
                raise ValueError("Cannot overwrite an original response; keep it and use a new exchange for another experiment")
            planned.append((entry, case, raw))
        # Capture every raw before parsing, including malformed JSON.
        invalid = 0
        for entry, case, raw in planned:
            self._capture(case, entry["request_sha256"], raw)
            request = json.loads((case / "request.json").read_bytes())
            try:
                self._parse(request, case, Extraction if entry["stage"] == "Extraction" else Verdict)
            except InvalidLLMResponse:
                invalid += 1
        return {"imported": len(planned), "invalid": invalid}

    def _call(self, stage: str, data: dict, contract, prompt: str):
        request, case = self.request(stage, data, contract, prompt)
        if not (case / "response.txt").exists() and self.interactive:
            entry = next(e for e in self._manifest()["requests"] if e["request_sha256"] == request["request_sha256"])
            print(f"=== LLM REQUEST {entry['filename']} / {stage} ===")
            print((case / "request.txt").read_text())
            print("Paste the ORIGINAL model response. Finish with END_JSON on its own line, or Ctrl+D.")
            lines = []
            for line in sys.stdin:
                if line.strip() == "END_JSON":
                    break
                lines.append(line)
            if not lines:
                raise PendingResponse(f"No response supplied; prompt saved at {case / 'request.txt'}")
            self._capture(case, request["request_sha256"], "".join(lines).encode("utf-8"))
        if not (case / "response.txt").exists():
            self.interactions.append({"stage": stage, "request_sha256": request["request_sha256"],
                                      "case_directory": str(case), "status": "pending"})
            raise PendingResponse(f"Manual ChatGPT response pending; copy prompt from {case / 'request.txt'}")
        return self._parse(request, case, contract)

    def extract(self, raw: str):
        return self._call("Extraction", {"document": raw}, Extraction,
                          EXTRACTION_PROMPT.format(taxonomy=", ".join(TAXONOMY)))

    def verify(self, proposal: Proposal):
        return self._call("Verdict", {"excerpt": proposal.source_span,
                                      "proposal": proposal.model_dump(mode="json")}, Verdict, VERIFICATION_PROMPT)
