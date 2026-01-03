"""Ollama provider for local LLM inference."""

from collections.abc import AsyncIterator
from typing import Any

import httpx
from ollama import AsyncClient

from brain.providers.base import LLMProviderBase
from core.config import LLMSettings


class OllamaProvider(LLMProviderBase):
    """Local LLM provider using Ollama."""

    def __init__(self, settings: LLMSettings) -> None:
        super().__init__(settings)
        self._client = AsyncClient(host=settings.ollama_base_url)
        self._available_models: list[str] | None = None

    async def list_models(self) -> list[str]:
        """List available models in Ollama."""
        if self._available_models is None:
            try:
                response = await self._client.list()
                self._available_models = [m["name"] for m in response.get("models", [])]
            except httpx.ConnectError:
                self._available_models = []
        return self._available_models

    async def ensure_model(self) -> bool:
        """Ensure the configured model is available."""
        models = await self.list_models()
        if self.settings.model not in models:
            try:
                await self._client.pull(self.settings.model)
                self._available_models = None
                return True
            except Exception:
                return False
        return True

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a response using Ollama."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        response = await self._client.chat(
            model=self.settings.model,
            messages=full_messages,
            options={
                "temperature": self.settings.temperature,
                "num_predict": self.settings.max_tokens,
            },
        )

        return response["message"]["content"]

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from Ollama."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        async for chunk in await self._client.chat(
            model=self.settings.model,
            messages=full_messages,
            stream=True,
            options={
                "temperature": self.settings.temperature,
                "num_predict": self.settings.max_tokens,
            },
        ):
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]
