"""Base class for LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from core.config import LLMSettings


class LLMProviderBase(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            messages: Conversation history as list of {role, content} dicts
            system: Optional system prompt
            tools: Optional list of available tools/functions

        Returns:
            The assistant's response text
        """
        ...

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the LLM.

        Yields text chunks as they're generated.
        """
        ...

    async def close(self) -> None:
        """Cleanup resources."""
        pass
