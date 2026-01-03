"""Tests for intent parsing."""

from brain.intent import IntentParser, IntentType


def test_home_control_turn_on() -> None:
    parser = IntentParser()
    intent = parser.parse("Turn on the living room lights")

    assert intent.type == IntentType.HOME_CONTROL
    assert intent.action == "power"
    assert intent.parameters["state"] == "on"
    assert "living room lights" in intent.parameters["device"]


def test_home_control_turn_off() -> None:
    parser = IntentParser()
    intent = parser.parse("Turn off the kitchen light")

    assert intent.type == IntentType.HOME_CONTROL
    assert intent.action == "power"
    assert intent.parameters["state"] == "off"


def test_home_control_set_level() -> None:
    parser = IntentParser()
    intent = parser.parse("Set the bedroom light to 50%")

    assert intent.type == IntentType.HOME_CONTROL
    assert intent.action == "set_level"
    assert intent.parameters["level"] == "50"


def test_system_volume() -> None:
    parser = IntentParser()
    intent = parser.parse("Set volume to 75")

    assert intent.type == IntentType.SYSTEM
    assert intent.action == "volume"
    assert intent.parameters["level"] == "75"


def test_system_media() -> None:
    parser = IntentParser()

    for action in ["pause", "play", "stop", "next", "previous"]:
        intent = parser.parse(action)
        assert intent.type == IntentType.SYSTEM
        assert intent.action == "media"
        assert intent.parameters["action"] == action


def test_vision_describe() -> None:
    parser = IntentParser()
    intent = parser.parse("What do you see?")

    assert intent.type == IntentType.VISION
    assert intent.action == "describe"


def test_conversation_fallback() -> None:
    parser = IntentParser()
    intent = parser.parse("Tell me about quantum physics")

    assert intent.type == IntentType.CONVERSATION


def test_is_question() -> None:
    parser = IntentParser()

    assert parser.is_question("What is the capital of France?")
    assert parser.is_question("How does this work")
    assert parser.is_question("Is it raining?")
    assert not parser.is_question("Turn on the lights")
