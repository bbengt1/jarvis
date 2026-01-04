# J.A.R.V.I.S. API Reference

> **Generated:** 2026-01-03

## Web API

Base URL: `http://localhost:8080`

### Settings

#### GET /api/settings

Returns current configuration (sensitive values masked).

**Response:**
```json
{
  "name": "Jarvis",
  "wake_word": "argus",
  "llm_provider": "ollama",
  "llm_model": "llama3.2",
  "llm_temperature": 0.7,
  "llm_max_tokens": 1024,
  "llm_ollama_base_url": "http://localhost:11434",
  "llm_openai_api_key_set": false,
  "llm_anthropic_api_key_set": true,
  "whisper_model": "base",
  "whisper_language": "en",
  "tts_voice": "en_US-lessac-medium",
  "tts_speed": 1.0,
  "vision_model": "yolov8n",
  "vision_camera_index": 0,
  "home_assistant_enabled": false,
  "home_assistant_url": "http://homeassistant.local:8123",
  "home_assistant_token_set": false,
  "mqtt_enabled": false,
  "mqtt_host": "localhost",
  "mqtt_port": 1883,
  "default_location": "New York"
}
```

#### POST /api/settings

Update configuration values.

**Request:**
```json
{
  "llm_provider": "anthropic",
  "llm_model": "claude-sonnet-4-20250514",
  "llm_anthropic_api_key": "sk-..."
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Settings updated"
}
```

---

### Providers

#### GET /api/providers

List available LLM providers and their models.

**Response:**
```json
{
  "providers": [
    {
      "id": "ollama",
      "name": "Ollama (Local)",
      "models": ["llama3.2", "llama3.1", "mistral", "codellama", "phi3"]
    },
    {
      "id": "openai",
      "name": "OpenAI",
      "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    },
    {
      "id": "anthropic",
      "name": "Anthropic (Claude)",
      "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
    },
    {
      "id": "google",
      "name": "Google (Gemini)",
      "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
    },
    {
      "id": "xai",
      "name": "xAI (Grok)",
      "models": ["grok-2-latest", "grok-beta"]
    }
  ]
}
```

---

### Status

#### GET /api/status

Get system status.

**Response:**
```json
{
  "status": "running",
  "platform": "Darwin",
  "python_version": "3.11.5",
  "settings_loaded": true
}
```

---

### Connection Testing

#### POST /api/test-connection

Test connection to external services.

**Request (Ollama):**
```json
{
  "service": "ollama",
  "url": "http://localhost:11434"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected! Found 3 models.",
  "models": ["llama3.2:latest", "mistral:latest", "codellama:latest"]
}
```

**Request (Home Assistant):**
```json
{
  "service": "home_assistant",
  "url": "http://homeassistant.local:8123",
  "token": "eyJ..."
}
```

---

### WebSocket

#### WS /ws/core

Real-time power core state updates.

**States:**
- `standby` - Idle, listening for wake word
- `listening` - Wake word detected, capturing command
- `processing` - Transcribing and generating response
- `speaking` - TTS output in progress

**Client to Server:**
```json
{"state": "listening"}
```

**Server to Client:**
```json
{"state": "processing"}
```

**Visualizer Data:**
```json
{"visualizer": [45, 78, 23, 89, 56, 12]}
```

---

## Python API

### LLMClient

```python
from brain.llm import LLMClient
from core.config import LLMSettings, LLMProvider

# Initialize
settings = LLMSettings(provider=LLMProvider.OLLAMA)
client = LLMClient(settings)

# Generate
messages = [{"role": "user", "content": "Hello"}]
response = await client.generate(messages)

# Stream
async for chunk in client.generate_stream(messages):
    print(chunk, end="")

# Switch provider
await client.switch_provider(LLMProvider.ANTHROPIC, "claude-sonnet-4-20250514")

# Cleanup
await client.close()
```

### HomeAutomation

```python
from home.automation import HomeAutomation
from core.config import HomeAssistantSettings, MQTTSettings

# Initialize
home = HomeAutomation(
    ha_settings=HomeAssistantSettings(url="http://ha.local:8123", token="..."),
    mqtt_settings=MQTTSettings(enabled=False)
)

# Refresh devices
devices = await home.refresh_devices()

# Find device (fuzzy match)
light = await home.get_device("living room light")

# Control
await home.turn_on(light, brightness=75)
await home.set_color(light, "warm")
await home.turn_off(light)

# Climate
await home.set_temperature("thermostat", 72)
await home.set_hvac_mode("thermostat", "cool")

# Media
await home.media_play("living room speaker")
await home.set_volume("living room speaker", 50)

# Scenes
await home.activate_scene("Movie Night")

# State summary
summary = await home.get_state_summary()
# {"lights": {"on": 3, "total": 12}, "locks": {...}, ...}

# Cleanup
await home.close()
```

### VisionProcessor

```python
from vision.processor import VisionProcessor
from core.config import VisionSettings

# Initialize
vision = VisionProcessor(VisionSettings())

# Capture and analyze
analysis = await vision.analyze_frame()
print(f"Found {len(analysis.detections)} objects")

# Describe scene
description = vision.describe_scene(analysis.detections)
# "I see 2 persons, a laptop, and a coffee cup."

# Stream analysis
async for analysis in vision.stream_analysis(interval=0.5):
    for det in analysis.detections:
        print(f"{det.label}: {det.confidence:.2f}")

# Cleanup
await vision.close()
```

### SpeechRecognizer

```python
from speech.recognition import SpeechRecognizer
from core.config import WhisperSettings

# Initialize
stt = SpeechRecognizer(WhisperSettings(model="base"))

# Transcribe audio bytes
text = await stt.transcribe(audio_data)

# Stream from microphone
async for text in stt.transcribe_stream():
    print(f"Heard: {text}")
```

### WakeWordDetector

```python
from speech.wakeword import WakeWordDetector
from core.config import Settings

# Initialize
detector = WakeWordDetector(Settings(wake_word="jarvis"))

# Listen for wake word
async for detection in detector.listen():
    print(f"Wake word: {detection.wake_word} ({detection.confidence:.2f})")
    if detection.audio_after is not None:
        # Process the audio captured after wake word
        text = await stt.transcribe(detection.audio_after)
```

### TextToSpeech

```python
from speech.synthesis import TextToSpeech
from core.config import TTSSettings

# Initialize
tts = TextToSpeech(TTSSettings())

# Speak text
await tts.speak("Hello, I am Jarvis.")

# Get audio bytes
audio_data = await tts.synthesize("Save this audio")
```

### SkillRegistry

```python
from skills.base import Skill, SkillResult, SkillRegistry
from core.context import ConversationContext

# Create custom skill
class GreetingSkill(Skill):
    name = "greeting"
    description = "Responds to greetings"

    async def can_handle(self, text: str, context) -> bool:
        return any(w in text.lower() for w in ["hello", "hi", "hey"])

    async def execute(self, text: str, context) -> SkillResult:
        return SkillResult(success=True, response="Hello! How can I help?")

# Register
registry = SkillRegistry()
registry.register(GreetingSkill(jarvis_instance))

# Execute
result = await registry.execute("Hello there", context)
if result:
    print(result.response)
```
