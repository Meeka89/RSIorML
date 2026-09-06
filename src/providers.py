"""Model backends.

Everything here targets the OpenAI-compatible /v1/chat/completions interface, which
vLLM, Ollama, llama.cpp's server, and TGI all expose. That keeps one code path for
locally hosted open-weight models and for hosted endpoints.

Configure with environment variables:

    BENCH_BASE_URL   default http://localhost:8000/v1
    BENCH_API_KEY    default "EMPTY" (local servers ignore it)
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_BASE_URL = os.environ.get("BENCH_BASE_URL", "http://localhost:8000/v1")
DEFAULT_API_KEY = os.environ.get("BENCH_API_KEY", "EMPTY")


class ProviderError(RuntimeError):
    pass


@dataclass
class ChatProvider:
    """One configured model. `name` is recorded in results and must be exact --
    including the revision -- so runs stay reproducible."""

    name: str
    base_url: str = DEFAULT_BASE_URL
    api_key: str = DEFAULT_API_KEY
    temperature: float = 0.0
    max_tokens: int = 1024
    timeout: int = 120
    max_retries: int = 3

    def complete(self, messages: list[dict], system: str | None = None) -> str:
        payload = {
            "model": self.name,
            "messages": ([{"role": "system", "content": system}] if system else []) + messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        last: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"] or ""
            except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError) as exc:
                last = exc
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        raise ProviderError(f"{self.name}: request failed after {self.max_retries} tries: {last}")


class EchoProvider(ChatProvider):
    """Offline stand-in so the pipeline can be exercised without a served model."""

    def complete(self, messages: list[dict], system: str | None = None) -> str:
        return f"[echo] {messages[-1]['content'][:120]}"


def get_provider(name: str, **kwargs) -> ChatProvider:
    if name == "echo":
        return EchoProvider(name="echo", **kwargs)
    return ChatProvider(name=name, **kwargs)
