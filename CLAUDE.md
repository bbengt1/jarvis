# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

J.A.R.V.I.S. is a real-life AI assistant inspired by the Iron Man AI, combining:
- **Wake Word Detection** - OpenWakeWord for always-on listening
- **Speech Recognition** - Whisper for local STT
- **Natural Language Processing** - Multi-provider LLM support (local + cloud)
- **Text-to-Speech** - Piper TTS (falls back to system TTS)
- **Computer Vision** - YOLO object detection via Ultralytics
- **Home Automation** - Full Home Assistant API + MQTT support
- **Skills** - Weather, calendar, reminders, and extensible framework
- **Web UI** - Browser-based configuration panel

Key design principles:
- **Local-first**: Core processing runs locally for privacy and low latency
- **Multi-provider LLM**: Supports Ollama (local), OpenAI, Anthropic, Google, and xAI
- **Async-first**: Non-blocking I/O for concurrent audio/vision/automation
- **Web-configurable**: All settings manageable via browser UI

## Commands

```bash
# Setup (requires uv)
uv sync                          # Install dependencies
uv sync --extra dev              # Install with dev dependencies

# Run
uv run jarvis                    # Start J.A.R.V.I.S. (voice interface)
uv run jarvis-web                # Start web configuration UI (port 8080)

# Run both (in separate terminals)
uv run jarvis-web &              # Web UI in background
uv run jarvis                    # Voice assistant

# Testing
uv run pytest                    # Run all tests
uv run pytest tests/test_intent.py -v           # Run specific test file
uv run pytest -k "test_home"     # Run tests matching pattern

# Linting & Formatting
uv run ruff check .              # Lint
uv run ruff check . --fix        # Lint with auto-fix
uv run ruff format .             # Format code
uv run mypy .                    # Type check
```

## Architecture

```
core/jarvis.py      # Central orchestrator - coordinates all subsystems
     context.py     # Conversation state with sliding window memory
     config.py      # Pydantic settings, LLMProvider enum

speech/wakeword.py    # OpenWakeWord detection for "Argus"
       recognition.py # Whisper STT with streaming audio capture
       synthesis.py   # TTS with Piper (macOS/Linux fallback)

brain/llm.py        # Multi-provider LLM client with unified interface
      intent.py     # Pattern-based intent parsing (fast path before LLM)
      providers/    # Provider implementations:
        base.py       # Abstract base class
        ollama.py     # Local inference via Ollama
        openai.py     # OpenAI API (GPT-4, etc.)
        anthropic.py  # Anthropic API (Claude)
        google.py     # Google Gemini API
        xai.py        # xAI Grok API

vision/processor.py # YOLO object detection, camera capture, scene description

home/automation.py  # Home Assistant REST API + MQTT client
                    # Supports: lights, locks, climate, media, covers, scenes

skills/base.py              # Skill interface and registry
       time_skill.py        # Time and date
       weather_skill.py     # Weather via Open-Meteo API (no key required)
       calendar_skill.py    # Local calendar with JSON storage
       reminder_skill.py    # Reminders with background checking
       argus_camera_skill.py # ArgusAI camera integration

web/server.py       # FastAPI web server
    templates/      # HTML templates for configuration UI
```

## Web Configuration UI

The web UI (http://localhost:8080) allows configuring:
- General: Assistant name, wake word
- LLM: Provider selection, model, API keys
- Speech: Whisper model, TTS voice
- Vision: YOLO model, camera selection
- Home: Home Assistant URL/token, MQTT settings
- Skills: Default location for weather

Settings are stored in `~/.jarvis/settings.json` and override `.env` values.

## LLM Provider System

The `LLMClient` in `brain/llm.py` provides a unified interface:

```python
# Switching providers at runtime
await llm.switch_provider(LLMProvider.ANTHROPIC, model="claude-sonnet-4-20250514")

# All providers support the same interface
response = await llm.generate(messages, system="Custom prompt")
async for chunk in llm.generate_stream(messages):
    print(chunk, end="")
```

## Home Automation

Enhanced `HomeAutomation` class supports:
- **Lights**: on/off, brightness, color (RGB or named)
- **Locks**: lock/unlock
- **Climate**: temperature, HVAC mode
- **Media**: play, pause, next, previous, volume
- **Covers**: blinds, garage doors with position control
- **Scenes**: activate by name
- **Automations**: trigger by name
- **Vacuums**: start, stop, return home

Fuzzy device matching: "living room light" finds "Living Room Ceiling Light"

## Adding Skills

1. Create `skills/my_skill.py` inheriting from `Skill`
2. Implement `can_handle()` and `execute()` methods
3. Register in `Jarvis.initialize()`

Example pattern:
```python
class MySkill(Skill):
    name = "my_skill"
    description = "Does something useful"

    async def can_handle(self, text: str, context) -> bool:
        return "my keyword" in text.lower()

    async def execute(self, text: str, context) -> SkillResult:
        return SkillResult(success=True, response="Done!")
```

## Data Storage

All persistent data stored in `~/.jarvis/`:
- `settings.json` - Web UI configuration
- `calendar.json` - Calendar events
- `reminders.json` - Active reminders

## ArgusAI Camera Integration

The `ArgusCameraSkill` integrates with ArgusAI for AI-powered security camera monitoring:

**Capabilities:**
- List cameras and their status
- Start/stop camera monitoring
- Get recent security events with AI descriptions
- Re-analyze events with AI

**Configuration:**
```bash
ARGUS_AI__ENABLED=true
ARGUS_AI__BASE_URL=http://localhost:8000/api/v1
ARGUS_AI__API_KEY=your_api_key
```

**Example queries (natural language):**
- "Is anyone at the front door?"
- "Check if there's a package on the porch"
- "What's going on in the driveway?"
- "Did you see anything suspicious outside?"
- "Is there a car in the garage?"
- "Start watching the backyard"
- "How many cameras do I have?"
- "Any visitors today?"
- "Look at that again" (re-analyze last event)

## External Dependencies

- **Ollama** (optional) - For local LLM: `ollama serve && ollama pull llama3.2`
- **API Keys** (optional) - Set via web UI or `.env` for cloud providers
- **Home Assistant** (optional) - Configure URL and token via web UI
- **ArgusAI** (optional) - AI-powered camera system at `http://localhost:8000`
- **Piper TTS** (optional) - Falls back to macOS `say` or Linux `espeak`
