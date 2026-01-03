"""Tests for conversation context."""

from core.context import ConversationContext


def test_add_message() -> None:
    ctx = ConversationContext(max_messages=5)
    ctx.add_user_message("Hello")
    ctx.add_assistant_message("Hi there!")

    assert len(ctx.messages) == 2
    assert ctx.messages[0].role == "user"
    assert ctx.messages[1].role == "assistant"


def test_sliding_window() -> None:
    ctx = ConversationContext(max_messages=3)

    for i in range(5):
        ctx.add_user_message(f"Message {i}")

    # Should only keep last 3
    assert len(ctx.messages) == 3
    assert ctx.messages[0].content == "Message 2"
    assert ctx.messages[2].content == "Message 4"


def test_get_messages_for_llm() -> None:
    ctx = ConversationContext()
    ctx.add_user_message("What's the weather?")
    ctx.add_assistant_message("I don't have weather data yet.")

    messages = ctx.get_messages_for_llm()

    assert messages == [
        {"role": "user", "content": "What's the weather?"},
        {"role": "assistant", "content": "I don't have weather data yet."},
    ]


def test_state_management() -> None:
    ctx = ConversationContext()

    ctx.set_state("user_name", "Tony")
    assert ctx.get_state("user_name") == "Tony"
    assert ctx.get_state("nonexistent") is None
    assert ctx.get_state("nonexistent", "default") == "default"


def test_last_messages() -> None:
    ctx = ConversationContext()
    ctx.add_user_message("First")
    ctx.add_assistant_message("Response 1")
    ctx.add_user_message("Second")

    assert ctx.last_user_message is not None
    assert ctx.last_user_message.content == "Second"
    assert ctx.last_assistant_message is not None
    assert ctx.last_assistant_message.content == "Response 1"
