# J.A.R.V.I.S. Documentation

> Just A Rather Very Intelligent System
> AI-powered voice assistant with home automation

**Version:** 0.1.0 | **Generated:** 2026-01-03 | **Type:** Brownfield Project

---

## Quick Start

```bash
# Install
uv sync

# Run voice assistant
uv run jarvis

# Run web configuration UI
uv run jarvis-web
```

---

## Documentation Index

### Core Documentation

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | System design, module reference, data models |
| [Project Context](project-context.md) | Critical patterns for AI agents |
| [API Reference](api-reference.md) | REST API and Python API documentation |

### Feature Guides

| Document | Description |
|----------|-------------|
| [Skills Guide](skills-guide.md) | Creating and extending skills |
| [LLM Providers](llm-providers.md) | Multi-provider LLM configuration |
| [Home Automation](home-automation.md) | Home Assistant & MQTT integration |

### Project Files

| File | Location | Purpose |
|------|----------|---------|
| README.md | `/` | User-facing overview |
| CLAUDE.md | `/` | AI assistant development guide |
| pyproject.toml | `/` | Dependencies and build config |

---

## Project Structure

```
jarvis/
├── core/           # Central orchestration
│   ├── jarvis.py   # Main entry point
│   ├── config.py   # Pydantic settings
│   └── context.py  # Conversation state
├── brain/          # NLP and LLM
│   ├── llm.py      # Multi-provider client
│   ├── intent.py   # Intent parsing
│   └── providers/  # LLM implementations
├── speech/         # Voice I/O
│   ├── wakeword.py # Wake word detection
│   ├── recognition.py # Whisper STT
│   └── synthesis.py   # Piper TTS
├── vision/         # Computer vision
│   └── processor.py   # YOLO detection
├── home/           # Smart home
│   └── automation.py  # HA + MQTT
├── skills/         # Capability framework
│   ├── base.py     # Skill interface
│   ├── weather_skill.py
│   ├── calendar_skill.py
│   └── ...
├── web/            # Configuration UI
│   ├── server.py   # FastAPI app
│   └── templates/  # HTML
├── tests/          # Test suite
└── docs/           # This documentation
```

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11+ |
| Package Manager | uv |
| Configuration | Pydantic v2 |
| Web Framework | FastAPI |
| LLM | Ollama, OpenAI, Anthropic, Google, xAI |
| Speech-to-Text | faster-whisper |
| Wake Word | OpenWakeWord |
| Text-to-Speech | Piper TTS |
| Vision | YOLO (Ultralytics) |
| Home Automation | Home Assistant, MQTT |
| Testing | pytest |
| Linting | ruff, mypy |

---

## Key Concepts

### Local-First Architecture
Core processing runs locally for privacy and low latency. Cloud LLM providers are optional.

### Multi-Provider LLM
Switch between Ollama (local), OpenAI, Anthropic, Google, or xAI at runtime.

### Async-First Design
All I/O is non-blocking for concurrent audio/vision/automation processing.

### Extensible Skills
Add new capabilities by implementing the `Skill` interface.

---

## Commands

| Command | Description |
|---------|-------------|
| `uv run jarvis` | Start voice assistant |
| `uv run jarvis-web` | Start web UI (port 8080) |
| `uv run pytest` | Run tests |
| `uv run ruff check .` | Lint code |
| `uv run mypy .` | Type check |

---

## Configuration

### Environment Variables (.env)

```bash
# General
NAME=Jarvis
WAKE_WORD=argus

# LLM Provider
LLM__PROVIDER=ollama
LLM__MODEL=llama3.2

# API Keys (cloud providers)
LLM__OPENAI_API_KEY=sk-...
LLM__ANTHROPIC_API_KEY=sk-ant-...

# Home Assistant
HOME_ASSISTANT__ENABLED=true
HOME_ASSISTANT__URL=http://homeassistant.local:8123
HOME_ASSISTANT__TOKEN=eyJ...
```

### Web UI

Access `http://localhost:8080` to configure all settings visually.

---

## Support

- **Project Repository:** Check CLAUDE.md for development guidelines
- **Architecture Questions:** See [Architecture](architecture.md)
- **Adding Features:** See [Skills Guide](skills-guide.md)
