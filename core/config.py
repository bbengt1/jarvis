"""Configuration management for J.A.R.V.I.S."""

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"


class WhisperSettings(BaseSettings):
    """Whisper speech recognition settings."""

    model: str = "base"  # tiny, base, small, medium, large
    language: str = "en"
    device: str = "auto"  # auto, cpu, cuda


class LLMSettings(BaseSettings):
    """LLM settings with multi-provider support."""

    # Provider selection
    provider: LLMProvider = LLMProvider.OLLAMA

    # Model name (provider-specific)
    model: str = "llama3.2"

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 1024

    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"

    # API keys (set via environment variables)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    xai_api_key: str = ""

    # Optional: custom base URLs for API-compatible endpoints
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_base_url: str = "https://api.anthropic.com"
    google_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    xai_base_url: str = "https://api.x.ai/v1"


class TTSSettings(BaseSettings):
    """Text-to-speech settings."""

    voice: str = "en_US-lessac-medium"
    speed: float = 1.0


class VisionSettings(BaseSettings):
    """Computer vision settings."""

    model: str = "yolov8n"  # nano model for speed
    camera_index: int = 0
    confidence_threshold: float = 0.5


class HomeAssistantSettings(BaseSettings):
    """Home Assistant integration settings."""

    url: str = "http://homeassistant.local:8123"
    token: str = ""
    enabled: bool = False


class MQTTSettings(BaseSettings):
    """MQTT broker settings for IoT devices."""

    host: str = "localhost"
    port: int = 1883
    username: str = ""
    password: str = ""
    enabled: bool = False


class ArgusAISettings(BaseSettings):
    """ArgusAI camera integration settings."""

    base_url: str = "http://localhost:8000/api/v1"
    api_key: str = ""
    enabled: bool = False
    websocket_url: str = "ws://localhost:8000/ws"


class Settings(BaseSettings):
    """Main configuration for J.A.R.V.I.S."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # General
    name: str = "Jarvis"
    wake_word: str = "argus"
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".jarvis")

    # Subsystems
    whisper: WhisperSettings = Field(default_factory=WhisperSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    vision: VisionSettings = Field(default_factory=VisionSettings)
    home_assistant: HomeAssistantSettings = Field(default_factory=HomeAssistantSettings)
    mqtt: MQTTSettings = Field(default_factory=MQTTSettings)
    argus_ai: ArgusAISettings = Field(default_factory=ArgusAISettings)

    # Performance
    use_gpu: bool = True
    max_context_messages: int = 20

    def ensure_data_dir(self) -> Path:
        """Ensure data directory exists and return it."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir
