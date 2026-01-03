"""Conversation and state context management."""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Manages conversation history and state.

    Uses a sliding window to maintain context while keeping memory bounded.
    """

    max_messages: int = 20
    messages: deque[Message] = field(default_factory=deque)
    state: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.messages = deque(self.messages, maxlen=self.max_messages)

    def add_message(self, role: str, content: str, **metadata: Any) -> Message:
        """Add a message to the conversation history."""
        msg = Message(role=role, content=content, metadata=metadata)
        self.messages.append(msg)
        return msg

    def add_user_message(self, content: str, **metadata: Any) -> Message:
        """Add a user message."""
        return self.add_message("user", content, **metadata)

    def add_assistant_message(self, content: str, **metadata: Any) -> Message:
        """Add an assistant message."""
        return self.add_message("assistant", content, **metadata)

    def get_messages_for_llm(self) -> list[dict[str, str]]:
        """Get messages formatted for LLM API."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()

    def set_state(self, key: str, value: Any) -> None:
        """Set a state value."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self.state.get(key, default)

    @property
    def last_user_message(self) -> Message | None:
        """Get the last user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg
        return None

    @property
    def last_assistant_message(self) -> Message | None:
        """Get the last assistant message."""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg
        return None
