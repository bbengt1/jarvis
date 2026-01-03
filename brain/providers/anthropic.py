"""Anthropic (Claude) provider."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from brain.providers.base import LLMProviderBase
from core.config import LLMSettings


class AnthropicProvider(LLMProviderBase):
    """Anthropic Claude API provider."""

    def __init__(self, settings: LLMSettings) -> None:
        super().__init__(settings)
        self._client = httpx.AsyncClient(
            base_url=settings.anthropic_base_url,
            headers={
                "x-api-key": settings.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            timeout=60.0,
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a response using Anthropic API."""
        # Anthropic uses a different message format
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": anthropic_messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
        }

        if system:
            payload["system"] = system

        if tools:
            # Convert to Anthropic tool format
            payload["tools"] = [
                {
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "input_schema": t["function"].get("parameters", {}),
                }
                for t in tools
                if "function" in t
            ]

        response = await self._client.post("/v1/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract text from content blocks
        text_parts = []
        for block in data.get("content", []):
            if block["type"] == "text":
                text_parts.append(block["text"])

        return "".join(text_parts)

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from Anthropic API."""
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": anthropic_messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
            "stream": True,
        }

        if system:
            payload["system"] = system

        async with self._client.stream("POST", "/v1/messages", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json

                    data = json.loads(line[6:])
                    if data["type"] == "content_block_delta":
                        if data["delta"]["type"] == "text_delta":
                            yield data["delta"]["text"]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
