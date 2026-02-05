from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class LLMClient:
    """
    Thin wrapper around an HTTP LLM API.

    This is intentionally minimal so it can be wired to:
    - OpenAI-style APIs
    - Local models
    - Enterprise gateways
    without changing core business logic.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url or os.getenv("DEADLINE_LLM_BASE_URL", "").rstrip("/")
        self.api_key = api_key or os.getenv("DEADLINE_LLM_API_KEY")
        self.model = model or os.getenv("DEADLINE_LLM_MODEL", "gpt-4.1-mini")
        self.timeout = timeout

        if not self.base_url:
            raise ValueError("LLM base URL is not configured (DEADLINE_LLM_BASE_URL).")

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generic chat-style call.

        The exact payload here assumes an OpenAI-compatible API.
        Adapt this to your actual provider if needed.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
        }

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected LLM response format: {data}") from exc

