"""Multi-provider LLM client."""

from collections.abc import AsyncIterator
from typing import Any

from brain.providers.base import LLMProviderBase
from brain.providers.anthropic import AnthropicProvider
from brain.providers.google import GoogleProvider
from brain.providers.ollama import OllamaProvider
from brain.providers.openai import OpenAIProvider
from brain.providers.xai import XAIProvider
from core.config import LLMProvider, LLMSettings

SYSTEM_PROMPT = """You are J.A.R.V.I.S., an advanced AI assistant inspired by the AI from Iron Man.
You are helpful, witty, and capable. You speak naturally and concisely.
You can control smart home devices, answer questions, and assist with various tasks.
Keep responses brief and conversational unless asked for detail."""

# Default models for each provider
DEFAULT_MODELS: dict[LLMProvider, str] = {
    LLMProvider.OLLAMA: "llama3.2",
    LLMProvider.OPENAI: "gpt-4o",
    LLMProvider.ANTHROPIC: "claude-sonnet-4-20250514",
    LLMProvider.GOOGLE: "gemini-1.5-flash",
    LLMProvider.XAI: "grok-2-latest",
}


class LLMClient:
    """Multi-provider LLM client.

    Supports switching between local (Ollama) and cloud providers
    (OpenAI, Anthropic, Google, xAI) with a unified interface.
    """

    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self._provider: LLMProviderBase | None = None

    def _get_provider(self) -> LLMProviderBase:
        """Get or create the configured provider."""
        if self._provider is None:
            provider_class: type[LLMProviderBase]

            match self.settings.provider:
                case LLMProvider.OLLAMA:
                    provider_class = OllamaProvider
                case LLMProvider.OPENAI:
                    provider_class = OpenAIProvider
                case LLMProvider.ANTHROPIC:
                    provider_class = AnthropicProvider
                case LLMProvider.GOOGLE:
                    provider_class = GoogleProvider
                case LLMProvider.XAI:
                    provider_class = XAIProvider
                case _:
                    raise ValueError(f"Unknown provider: {self.settings.provider}")

            self._provider = provider_class(self.settings)

        return self._provider

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a response from the configured LLM provider.

        Args:
            messages: Conversation history as list of {role, content} dicts
            system: Optional system prompt override
            tools: Optional list of available tools/functions

        Returns:
            The assistant's response text
        """
        provider = self._get_provider()
        return await provider.generate(
            messages=messages,
            system=system or SYSTEM_PROMPT,
            tools=tools,
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the configured LLM provider.

        Yields text chunks as they're generated.
        """
        provider = self._get_provider()
        async for chunk in provider.generate_stream(
            messages=messages,
            system=system or SYSTEM_PROMPT,
        ):
            yield chunk

    async def switch_provider(self, provider: LLMProvider, model: str | None = None) -> None:
        """Switch to a different provider at runtime.

        Args:
            provider: The new provider to use
            model: Optional model name (uses default if not specified)
        """
        # Close existing provider
        if self._provider:
            await self._provider.close()
            self._provider = None

        # Update settings
        self.settings.provider = provider
        if model:
            self.settings.model = model
        else:
            self.settings.model = DEFAULT_MODELS.get(provider, "")

    async def close(self) -> None:
        """Cleanup resources."""
        if self._provider:
            await self._provider.close()
            self._provider = None
