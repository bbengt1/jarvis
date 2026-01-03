"""Google Gemini provider."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from brain.providers.base import LLMProviderBase
from core.config import LLMSettings


class GoogleProvider(LLMProviderBase):
    """Google Gemini API provider."""

    def __init__(self, settings: LLMSettings) -> None:
        super().__init__(settings)
        self._client = httpx.AsyncClient(
            base_url=settings.google_base_url,
            timeout=60.0,
        )
        self._api_key = settings.google_api_key

    def _convert_messages(
        self, messages: list[dict[str, str]], system: str | None
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Convert messages to Gemini format."""
        gemini_contents = []

        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })

        return gemini_contents, system

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a response using Gemini API."""
        contents, system_instruction = self._convert_messages(messages, system)

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.settings.temperature,
                "maxOutputTokens": self.settings.max_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"/models/{self.settings.model}:generateContent?key={self._api_key}"
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract text from response
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")

        return ""

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from Gemini API."""
        contents, system_instruction = self._convert_messages(messages, system)

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.settings.temperature,
                "maxOutputTokens": self.settings.max_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"/models/{self.settings.model}:streamGenerateContent?key={self._api_key}&alt=sse"

        async with self._client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json

                    data = json.loads(line[6:])
                    candidates = data.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if parts:
                            yield parts[0].get("text", "")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
