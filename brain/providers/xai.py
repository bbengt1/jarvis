"""xAI (Grok) provider."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from brain.providers.base import LLMProviderBase
from core.config import LLMSettings


class XAIProvider(LLMProviderBase):
    """xAI Grok API provider.

    Uses OpenAI-compatible API format.
    """

    def __init__(self, settings: LLMSettings) -> None:
        super().__init__(settings)
        self._client = httpx.AsyncClient(
            base_url=settings.xai_base_url,
            headers={
                "Authorization": f"Bearer {settings.xai_api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a response using xAI API."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": full_messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }

        if tools:
            payload["tools"] = tools

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from xAI API."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model": self.settings.model,
            "messages": full_messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
            "stream": True,
        }

        async with self._client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json

                    chunk = json.loads(data)
                    if chunk["choices"][0]["delta"].get("content"):
                        yield chunk["choices"][0]["delta"]["content"]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
