"""Ollama provider (local models via HTTP API)."""

from __future__ import annotations

import json
import time
import urllib.request

from inspektorium.audit.providers import BaseProvider
from inspektorium.audit.providers.response import ModelResponse, classify_error_type
from inspektorium.audit.schemas import Task

# Ollama done_reason -> normalized finish_reason (only mapped when present;
# never fabricated).
_DONE_REASON_MAP = {
    "stop": "stop",
    "length": "length",
}


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434",
                 temperature: float = 0.0, label: str = ""):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.label = label or model

    def generate(self, task: Task, system_prompt: str) -> ModelResponse:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task.prompt},
            ],
            "stream": False,
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            latency = int((time.monotonic() - start) * 1000)

            text = data.get("message", {}).get("content", "")

            # done_reason is only present on newer Ollama versions; do not guess.
            raw_reason = data.get("done_reason")
            finish_reason = _DONE_REASON_MAP.get(raw_reason) if raw_reason else None

            usage = None
            if "prompt_eval_count" in data or "eval_count" in data:
                usage = {
                    "prompt_tokens": data.get("prompt_eval_count"),
                    "completion_tokens": data.get("eval_count"),
                }
            return ModelResponse(
                text=text,
                provider=self.name,
                model=self.model,
                finish_reason=finish_reason,
                usage=usage,
                latency_ms=latency,
            )
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return ModelResponse(
                text="",
                provider=self.name,
                model=self.model,
                finish_reason="error",
                latency_ms=latency,
                error=f"Ollama request failed: {e}",
                error_type=classify_error_type(e),
            )

    def send_prompt(self, task: Task, system_prompt: str) -> str:
        resp = self.generate(task, system_prompt)
        if resp.error:
            raise RuntimeError(resp.error)
        return resp.text
