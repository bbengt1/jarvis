# J.A.R.V.I.S. Architecture Documentation

> **Generated:** 2026-01-03
> **Project Type:** Backend (Python Application)
> **Version:** 0.1.0

## Overview

J.A.R.V.I.S. (Just A Rather Very Intelligent System) is a real-life AI assistant inspired by the Iron Man AI, designed as a local-first, privacy-respecting voice assistant with home automation capabilities.

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Local-First** | Core processing runs locally for privacy and low latency |
| **Multi-Provider LLM** | Supports Ollama (local), OpenAI, Anthropic, Google, xAI |
| **Async-First** | Non-blocking I/O for concurrent audio/vision/automation |
| **Web-Configurable** | All settings manageable via browser UI |
| **Extensible Skills** | Modular skill framework for adding capabilities |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        J.A.R.V.I.S.                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │   Speech    │     │    Brain    │     │   Vision    │      │
│   │  (STT/TTS)  │────▶│   (LLM)     │◀────│   (YOLO)    │      │
│   └─────────────┘     └─────────────┘     └─────────────┘      │
│          │                   │                   │              │
│          ▼                   ▼                   ▼              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │  Wake Word  │     │   Skills    │     │   ArgusAI   │      │
│   │ (OpenWake)  │     │  Framework  │     │  Cameras    │      │
│   └─────────────┘     └─────────────┘     └─────────────┘      │
│                              │                                  │
│                              ▼                                  │
│                       ┌─────────────┐                          │
│                       │    Home     │                          │
│                       │ Automation  │                          │
│                       └─────────────┘                          │
│                              │                                  │
├──────────────────────────────┼──────────────────────────────────┤
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    Web UI (FastAPI)                      │  │
│   │           Configuration & Status Dashboard               │  │
│   └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Reference

### Core (`core/`)

The central orchestration layer that coordinates all subsystems.

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `jarvis.py` | Main entry point and orchestrator | `Jarvis`, `async_main()`, `main()` |
| `config.py` | Configuration with Pydantic | `Settings`, `LLMSettings`, `LLMProvider` |
| `context.py` | Conversation state management | `ConversationContext`, `Message` |

**Jarvis Class** (`core/jarvis.py:11`)
- Central coordinator for all subsystems
- Manages async event loop for concurrent inputs
- Entry points: `jarvis` (CLI), `jarvis-web` (server)

**Settings System** (`core/config.py:99`)
- Pydantic v2 with `pydantic-settings` for env loading
- Nested settings: `LLMSettings`, `WhisperSettings`, `VisionSettings`, etc.
- Environment variables via `.env` with `__` delimiter for nesting

---

### Brain (`brain/`)

Natural language processing and LLM integration.

| File | Purpose | Key Classes |
|------|---------|-------------|
| `llm.py` | Multi-provider LLM client | `LLMClient` |
| `intent.py` | Pattern-based intent parsing | `IntentParser`, `Intent`, `IntentType` |
| `providers/*.py` | Provider implementations | `LLMProviderBase`, specific providers |

**LLM Provider System** (`brain/llm.py:29`)

```python
# Runtime provider switching
await llm.switch_provider(LLMProvider.ANTHROPIC, model="claude-sonnet-4-20250514")

# Unified interface for all providers
response = await llm.generate(messages, system="Custom prompt")
async for chunk in llm.generate_stream(messages):
    print(chunk, end="")
```

**Supported Providers:**

| Provider | Default Model | Base URL |
|----------|--------------|----------|
| Ollama | llama3.2 | localhost:11434 |
| OpenAI | gpt-4o | api.openai.com |
| Anthropic | claude-sonnet-4-20250514 | api.anthropic.com |
| Google | gemini-1.5-flash | generativelanguage.googleapis.com |
| xAI | grok-2-latest | api.x.ai |

**Intent Parser** (`brain/intent.py:31`)
- Fast pattern matching before LLM fallback
- Intent types: `HOME_CONTROL`, `SYSTEM`, `VISION`, `CONVERSATION`
- Regex-based extraction of actions and parameters

---

### Speech (`speech/`)

Voice input and output processing.

| File | Purpose | Key Classes |
|------|---------|-------------|
| `wakeword.py` | Always-on wake word detection | `WakeWordDetector`, `WakeWordDetection` |
| `recognition.py` | Speech-to-text | `SpeechRecognizer` |
| `synthesis.py` | Text-to-speech | `TextToSpeech` |

**Wake Word Detection** (`speech/wakeword.py:24`)
- Uses OpenWakeWord with ONNX inference
- Configurable wake word (default: "argus")
- Captures audio after detection for transcription
- 80ms chunk size at 16kHz

**Speech Recognition** (`speech/recognition.py:13`)
- faster-whisper for local STT
- Model sizes: tiny, base, small, medium, large
- Auto device selection (CUDA/CPU)
- VAD filtering enabled

**Text-to-Speech** (`speech/synthesis.py:16`)
- Primary: Piper TTS (local neural TTS)
- Fallback: macOS `say` / Linux `espeak`
- 22050Hz output sample rate

---

### Vision (`vision/`)

Computer vision and camera processing.

| File | Purpose | Key Classes |
|------|---------|-------------|
| `processor.py` | YOLO object detection | `VisionProcessor`, `Detection`, `FrameAnalysis` |

**Vision Processor** (`vision/processor.py:33`)
- YOLO via Ultralytics (yolov8n default)
- OpenCV camera capture (640x480)
- Natural language scene description
- Async frame streaming

```python
# Analyze current camera view
analysis = await vision.analyze_frame()
description = vision.describe_scene(analysis.detections)
# Output: "I see 2 persons, a laptop, and a coffee cup."
```

---

### Home Automation (`home/`)

Smart home integration.

| File | Purpose | Key Classes |
|------|---------|-------------|
| `automation.py` | Home Assistant + MQTT | `HomeAutomation`, `Device`, `DeviceType` |

**Home Automation** (`home/automation.py:75`)

**Supported Device Types:**
- Lights: on/off, brightness (0-100), color (RGB or named)
- Locks: lock/unlock
- Climate: temperature, HVAC mode (heat/cool/auto/off)
- Media Players: play, pause, next, previous, volume
- Covers: blinds, garage doors with position control
- Vacuums: start, stop, return home
- Scenes: activate by name
- Automations: trigger by name

**Fuzzy Device Matching:**
```python
# "living room light" matches "Living Room Ceiling Light"
device = await home.get_device("living room light")
await home.turn_on(device, brightness=75)
```

**MQTT Support:**
```python
await home.connect_mqtt()
await home.publish_mqtt("zigbee/light/set", '{"state": "ON"}')
```

---

### Skills (`skills/`)

Extensible capability framework.

| File | Purpose | Key Classes |
|------|---------|-------------|
| `base.py` | Skill interface | `Skill`, `SkillResult`, `SkillRegistry` |
| `time_skill.py` | Time and date queries | `TimeSkill` |
| `weather_skill.py` | Weather via Open-Meteo | `WeatherSkill` |
| `calendar_skill.py` | Local calendar | `CalendarSkill` |
| `reminder_skill.py` | Reminder management | `ReminderSkill` |
| `argus_camera_skill.py` | ArgusAI integration | `ArgusCameraSkill` |

**Skill Interface** (`skills/base.py:22`)

```python
class MySkill(Skill):
    name = "my_skill"
    description = "Does something useful"

    async def can_handle(self, text: str, context) -> bool:
        return "my keyword" in text.lower()

    async def execute(self, text: str, context) -> SkillResult:
        return SkillResult(success=True, response="Done!")
```

**Skill Execution Flow:**
1. `SkillRegistry.find_skill()` checks each skill's `can_handle()`
2. First matching skill's `execute()` is called
3. Returns `SkillResult` with response and optional data

---

### Web (`web/`)

Configuration UI and API.

| File | Purpose | Key Classes |
|------|---------|-------------|
| `server.py` | FastAPI application | `create_app()`, `SettingsManager` |
| `templates/` | HTML templates | `index.html`, `core.html` |
| `static/` | Static assets | CSS, JS |

**Web Server** (`web/server.py:217`)
- FastAPI with lifespan management
- WebSocket for real-time core state updates
- JSON settings persistence in `~/.jarvis/settings.json`

**API Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Configuration UI |
| `/core` | GET | Power core visualization |
| `/ws/core` | WS | Real-time state updates |
| `/api/settings` | GET/POST | Settings management |
| `/api/providers` | GET | List LLM providers |
| `/api/status` | GET | System status |
| `/api/test-connection` | POST | Test Ollama/HA connection |

---

## Data Models

### Conversation Message (`core/context.py:9`)
```python
@dataclass
class Message:
    role: str           # "user", "assistant", "system"
    content: str
    timestamp: datetime
    metadata: dict[str, Any]
```

### Device (`home/automation.py:32`)
```python
@dataclass
class Device:
    entity_id: str        # e.g., "light.living_room"
    name: str             # Friendly name
    device_type: DeviceType
    state: str            # "on", "off", "unavailable"
    attributes: dict
```

### Detection (`vision/processor.py:14`)
```python
@dataclass
class Detection:
    label: str            # Object class
    confidence: float     # 0.0 - 1.0
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    center: tuple[int, int]
```

### Intent (`brain/intent.py:18`)
```python
@dataclass
class Intent:
    type: IntentType
    action: str | None
    target: str | None
    parameters: dict[str, str]
    confidence: float
    raw_text: str
```

---

## External Integrations

### Home Assistant
- REST API at configured URL
- Long-lived access token authentication
- Device discovery via `/api/states`
- Service calls via `/api/services/{domain}/{service}`

### MQTT
- aiomqtt async client
- Optional username/password auth
- Direct device control for IoT devices

### ArgusAI Camera System
- REST API at `http://localhost:8000/api/v1`
- WebSocket at `ws://localhost:8000/ws`
- AI-powered security camera events
- Event re-analysis capability

### Open-Meteo Weather API
- No API key required
- Location-based forecasts
- Used by WeatherSkill

---

## Data Storage

All persistent data in `~/.jarvis/`:

| File | Purpose |
|------|---------|
| `settings.json` | Web UI configuration |
| `calendar.json` | Calendar events |
| `reminders.json` | Active reminders |

---

## Entry Points

| Command | Script | Description |
|---------|--------|-------------|
| `jarvis` | `core.jarvis:main` | Voice assistant CLI |
| `jarvis-web` | `web.server:run_server` | Web configuration UI (port 8080) |

---

## Development

### Setup
```bash
uv sync                    # Install dependencies
uv sync --extra dev        # With dev dependencies
```

### Testing
```bash
uv run pytest              # All tests
uv run pytest -v           # Verbose
uv run pytest -k "intent"  # Pattern match
```

### Code Quality
```bash
uv run ruff check .        # Lint
uv run ruff check . --fix  # Auto-fix
uv run ruff format .       # Format
uv run mypy .              # Type check (strict)
```

### Configuration
Tool configs in `pyproject.toml`:
- Ruff: line-length=100, target py311
- mypy: strict mode
- pytest: asyncio_mode="auto"

---

## Dependencies

### Core
- pydantic>=2.0 - Settings validation
- pydantic-settings>=2.0 - Env loading
- httpx>=0.27 - Async HTTP client

### Speech
- faster-whisper>=1.0 - Local STT
- openwakeword>=0.6 - Wake word
- piper-tts>=1.2 - Neural TTS
- sounddevice>=0.4 - Audio capture
- numpy>=1.24 - Audio processing

### LLM
- ollama>=0.3 - Local inference

### Vision
- opencv-python>=4.9 - Camera capture
- ultralytics>=8.0 - YOLO models

### Home
- aiomqtt>=2.0 - MQTT client
- aiohttp>=3.9 - HA API

### Web
- fastapi>=0.110 - REST API
- uvicorn[standard]>=0.29 - ASGI server
- websockets>=12.0 - Real-time updates

### Dev
- pytest>=8.0
- pytest-asyncio>=0.23
- ruff>=0.5
- mypy>=1.10
