# J.A.R.V.I.S.

A real-life AI assistant inspired by Iron Man's J.A.R.V.I.S., combining wake word detection, speech recognition, natural language processing, computer vision, and home automation.

## Features

- **Wake Word Detection** - Always-on listening with OpenWakeWord ("Argus")
- **Speech Recognition** - Local voice processing with OpenAI Whisper
- **Natural Language Processing** - Multi-provider LLM support:
  - **Local**: Ollama (llama3.2, mistral, etc.)
  - **Cloud**: OpenAI, Anthropic (Claude), Google (Gemini), xAI (Grok)
- **Text-to-Speech** - Neural TTS with Piper (falls back to system TTS)
- **Computer Vision** - Real-time object detection with YOLO
- **Home Automation** - Full Home Assistant integration with MQTT
- **Built-in Skills** - Weather, calendar, reminders, time
- **Web Configuration UI** - Browser-based settings panel
- **Power Core Display** - Arc reactor visualization that responds to voice

All core processing runs locally for privacy and low latency.

## Getting Started

### Prerequisites

- Python 3.11-3.13 (3.14 not yet supported by dependencies)
- [uv](https://github.com/astral-sh/uv) package manager
- Microphone and speakers
- **One of**:
  - [Ollama](https://ollama.ai) for local LLM inference
  - API key for a cloud provider (OpenAI, Anthropic, Google, or xAI)

### Installation

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and enter the project
cd jarvis

# Install dependencies
uv sync --extra dev

# Start the web configuration UI
uv run jarvis-web

# Open http://localhost:8080 in your browser to configure settings
```

### Configuration

**Option 1: Web UI (Recommended)**

1. Run `uv run jarvis-web`
2. Open http://localhost:8080
3. Configure your LLM provider, API keys, and other settings
4. Settings are saved automatically

**Option 2: Environment Variables**

Copy `.env.example` to `.env` and edit:

```bash
# Local with Ollama
LLM__PROVIDER=ollama
LLM__MODEL=llama3.2

# Or cloud provider
LLM__PROVIDER=anthropic
LLM__MODEL=claude-sonnet-4-20250514
LLM__ANTHROPIC_API_KEY=sk-ant-...
```

### Running

```bash
# Terminal 1: Web UI for configuration
uv run jarvis-web

# Terminal 2: Voice assistant
uv run jarvis
```

Then say "Argus" followed by your command!

## Usage Examples

- "Argus, what time is it?"
- "Argus, how's the weather looking today?"
- "Argus, remind me to call mom in half an hour"
- "Argus, I have a meeting tomorrow at 2"
- "Argus, can you turn on the living room lights?"
- "Argus, it's a bit cold in here" (adjusts thermostat)
- "Argus, what do you see?" (with camera enabled)
- "Argus, is anyone at the front door?"

## Skills

| Skill | Description |
|-------|-------------|
| **Time** | Current time and date |
| **Weather** | Weather and forecasts (no API key needed) |
| **Calendar** | Create, list, and manage events |
| **Reminders** | Set and manage reminders with notifications |
| **Home** | Control lights, locks, thermostats, media, and more |
| **Vision** | Describe what the camera sees |
| **ArgusAI** | AI-powered security camera monitoring and events |

## Home Automation

Supports Home Assistant with:
- **Lights**: On/off, brightness, color
- **Locks**: Lock/unlock
- **Climate**: Temperature, HVAC mode
- **Media**: Play, pause, volume, next/previous
- **Covers**: Blinds, garage doors
- **Scenes**: Activate by name
- **Vacuums**: Start, stop, return home

Configure in the web UI under "Home Automation".

## ArgusAI Camera Integration

Integrates with [ArgusAI](https://github.com/project-argusai/ArgusAI) for AI-powered security camera monitoring:

- **Camera Management**: List, start, and stop cameras
- **Event Detection**: View AI-analyzed security events
- **Re-analysis**: Re-analyze events with different AI providers

Example queries:
- "Argus, is anyone at the front door?"
- "Argus, check if there's a package on the porch"
- "Argus, what's going on in the driveway?"
- "Argus, did you see anything outside?"
- "Argus, start watching the backyard"
- "Argus, any visitors today?"

Configure in `.env`:
```bash
ARGUS_AI__ENABLED=true
ARGUS_AI__BASE_URL=http://localhost:8000/api/v1
ARGUS_AI__API_KEY=your_api_key
```

## Power Core Display

The Power Core page (`/core`) provides an Iron Man-inspired arc reactor visualization:

- **Arc reactor design** with rotating rings and energy arcs
- **Voice-responsive** - glows and pulses when Argus speaks or listens
- **Audio visualizer** - real-time frequency bars
- **Microphone input** - click the core or press Space to enable
- **Status indicators** - STANDBY, LISTENING, THINKING, SPEAKING

Access it at http://localhost:8080/core or click "Power Core" in the settings header.

## Architecture

```
core/           # Central orchestrator, config, context
speech/         # Wake word, Whisper STT, Piper TTS
brain/          # Multi-provider LLM client + intent parsing
  providers/    # Ollama, OpenAI, Anthropic, Google, xAI
vision/         # YOLO object detection
home/           # Home Assistant + MQTT
skills/         # Time, weather, calendar, reminders, ArgusAI
web/            # FastAPI server + UI
  templates/    # Settings page, Power Core display
```

## License

MIT
