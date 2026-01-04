# Skills Development Guide

> How to create and extend J.A.R.V.I.S. capabilities

## Overview

Skills are modular capabilities that can handle specific user intents. When a user speaks a command, the skill registry finds the appropriate skill and executes it.

## Built-in Skills

| Skill | File | Description |
|-------|------|-------------|
| TimeSkill | `skills/time_skill.py` | Time and date queries |
| WeatherSkill | `skills/weather_skill.py` | Weather via Open-Meteo API |
| CalendarSkill | `skills/calendar_skill.py` | Local calendar management |
| ReminderSkill | `skills/reminder_skill.py` | Set and check reminders |
| ArgusCameraSkill | `skills/argus_camera_skill.py` | AI camera integration |

## Creating a Skill

### 1. Create the File

```python
# skills/my_skill.py
"""My custom skill."""

from skills.base import Skill, SkillResult


class MySkill(Skill):
    """A custom skill for J.A.R.V.I.S."""

    name = "my_skill"
    description = "Does something amazing"
    triggers = ["amazing", "cool"]  # Optional: keywords for discovery
```

### 2. Implement can_handle()

This method determines if your skill should process the input.

```python
async def can_handle(self, text: str, context: "ConversationContext") -> bool:
    """Check if this skill can handle the input."""
    text_lower = text.lower()

    # Simple keyword matching
    return any(trigger in text_lower for trigger in [
        "do something amazing",
        "show me something cool",
        "demonstrate",
    ])
```

### 3. Implement execute()

This method performs the skill's action.

```python
async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
    """Execute the skill."""
    try:
        # Your skill logic here
        result = await self._do_amazing_thing()

        return SkillResult(
            success=True,
            response=f"Here's something amazing: {result}",
            data={"result": result},
            speak=True  # Set False to suppress TTS
        )
    except Exception as e:
        return SkillResult(
            success=False,
            response=f"Sorry, I couldn't do that: {e}"
        )
```

### 4. Register the Skill

In `core/jarvis.py`, add to the `initialize()` method:

```python
from skills.my_skill import MySkill

# In Jarvis.initialize():
self._skills_registry.register(MySkill(self))
```

## SkillResult Fields

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `success` | bool | Required | Whether execution succeeded |
| `response` | str | Required | Text response to user |
| `data` | dict | `{}` | Additional data for other systems |
| `speak` | bool | `True` | Whether to speak the response |

## Accessing Jarvis Systems

Skills receive a reference to the Jarvis instance:

```python
class MySkill(Skill):
    def __init__(self, jarvis: "Jarvis") -> None:
        super().__init__(jarvis)
        # self.jarvis is now available

    async def execute(self, text: str, context) -> SkillResult:
        # Access LLM
        llm = self.jarvis._subsystems.get("llm")
        response = await llm.generate([{"role": "user", "content": text}])

        # Access Home Automation
        home = self.jarvis._subsystems.get("home")
        if home:
            await home.turn_on("living room light")

        # Access Vision
        vision = self.jarvis._subsystems.get("vision")
        if vision:
            analysis = await vision.analyze_frame()
```

## Using Conversation Context

The context provides conversation history and state:

```python
async def execute(self, text: str, context: ConversationContext) -> SkillResult:
    # Get last user message
    last_msg = context.last_user_message

    # Check state
    if context.get_state("my_skill_active"):
        # Continue previous interaction
        pass

    # Set state for next interaction
    context.set_state("my_skill_active", True)

    # Get formatted history for LLM
    messages = context.get_messages_for_llm()
```

## Example: Weather Skill

Here's how the built-in weather skill works:

```python
class WeatherSkill(Skill):
    name = "weather"
    description = "Get current weather and forecasts"

    def __init__(self, jarvis: "Jarvis", default_location: str = "New York") -> None:
        super().__init__(jarvis)
        self.default_location = default_location

    async def can_handle(self, text: str, context) -> bool:
        weather_words = ["weather", "temperature", "forecast", "rain", "sunny"]
        return any(word in text.lower() for word in weather_words)

    async def execute(self, text: str, context) -> SkillResult:
        # Extract location or use default
        location = self._extract_location(text) or self.default_location

        # Fetch weather (Open-Meteo API - no key needed)
        weather = await self._fetch_weather(location)

        response = (
            f"The weather in {location} is {weather['condition']} "
            f"with a temperature of {weather['temp']}°F."
        )

        return SkillResult(success=True, response=response)
```

## Best Practices

### 1. Keep can_handle() Fast

Avoid heavy operations in `can_handle()`. Use simple string matching.

```python
# Good
async def can_handle(self, text: str, context) -> bool:
    return "weather" in text.lower()

# Avoid - too slow
async def can_handle(self, text: str, context) -> bool:
    # Don't call APIs or do heavy parsing here
    response = await llm.generate(...)  # Bad!
```

### 2. Handle Errors Gracefully

Always catch exceptions and return helpful error messages.

```python
async def execute(self, text: str, context) -> SkillResult:
    try:
        result = await self.risky_operation()
        return SkillResult(success=True, response=str(result))
    except ConnectionError:
        return SkillResult(
            success=False,
            response="I couldn't connect to the service. Please try again."
        )
    except Exception as e:
        return SkillResult(
            success=False,
            response=f"Something went wrong: {e}"
        )
```

### 3. Use Async Operations

All external calls should be async.

```python
# Good
async def _fetch_data(self) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(self.api_url)
        return response.json()

# Avoid - blocks event loop
def _fetch_data(self) -> dict:
    response = requests.get(self.api_url)  # Blocking!
    return response.json()
```

### 4. Keep Responses Conversational

Match J.A.R.V.I.S. personality - helpful, witty, concise.

```python
# Good
response = "It's currently 72°F and sunny. Perfect for a walk!"

# Avoid - too robotic
response = "Temperature: 72. Condition: sunny."
```

## Testing Skills

```python
# tests/test_my_skill.py
import pytest
from skills.my_skill import MySkill
from core.context import ConversationContext


@pytest.fixture
def skill():
    # Mock jarvis instance if needed
    return MySkill(jarvis=None)


@pytest.fixture
def context():
    return ConversationContext()


async def test_can_handle_positive(skill, context):
    assert await skill.can_handle("do something amazing", context)


async def test_can_handle_negative(skill, context):
    assert not await skill.can_handle("random text", context)


async def test_execute_success(skill, context):
    result = await skill.execute("do something amazing", context)
    assert result.success
    assert "amazing" in result.response.lower()
```

## Skill Priority

Skills are checked in registration order. Register more specific skills first:

```python
# In Jarvis.initialize():
registry.register(SpecificCameraSkill(self))  # First - specific
registry.register(GeneralVisionSkill(self))   # Second - general
```
