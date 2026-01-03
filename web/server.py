"""FastAPI web server for J.A.R.V.I.S. configuration UI."""

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import asyncio

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.config import LLMProvider, Settings


class SettingsUpdate(BaseModel):
    """Model for settings updates."""

    # General
    name: str | None = None
    wake_word: str | None = None

    # LLM
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_temperature: float | None = None
    llm_max_tokens: int | None = None
    llm_ollama_base_url: str | None = None
    llm_openai_api_key: str | None = None
    llm_anthropic_api_key: str | None = None
    llm_google_api_key: str | None = None
    llm_xai_api_key: str | None = None

    # Whisper
    whisper_model: str | None = None
    whisper_language: str | None = None

    # TTS
    tts_voice: str | None = None
    tts_speed: float | None = None

    # Vision
    vision_enabled: bool | None = None
    vision_model: str | None = None
    vision_camera_index: int | None = None

    # Home Assistant
    home_assistant_enabled: bool | None = None
    home_assistant_url: str | None = None
    home_assistant_token: str | None = None

    # MQTT
    mqtt_enabled: bool | None = None
    mqtt_host: str | None = None
    mqtt_port: int | None = None
    mqtt_username: str | None = None
    mqtt_password: str | None = None

    # Skills
    default_location: str | None = None


class SettingsManager:
    """Manages persistent settings with JSON storage."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.settings_path = data_dir / "settings.json"
        self._settings: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load settings from disk."""
        if self.settings_path.exists():
            try:
                self._settings = json.loads(self.settings_path.read_text())
            except Exception:
                self._settings = {}

    def _save(self) -> None:
        """Save settings to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(json.dumps(self._settings, indent=2))

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings[key] = value
        self._save()

    def update(self, updates: dict[str, Any]) -> None:
        """Update multiple settings."""
        for key, value in updates.items():
            if value is not None:
                self._settings[key] = value
        self._save()

    def get_all(self) -> dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()

    def apply_to_config(self, settings: Settings) -> Settings:
        """Apply stored settings to a Settings object."""
        # LLM settings
        if provider := self.get("llm_provider"):
            try:
                settings.llm.provider = LLMProvider(provider)
            except ValueError:
                pass

        if model := self.get("llm_model"):
            settings.llm.model = model
        if temp := self.get("llm_temperature"):
            settings.llm.temperature = temp
        if tokens := self.get("llm_max_tokens"):
            settings.llm.max_tokens = tokens
        if url := self.get("llm_ollama_base_url"):
            settings.llm.ollama_base_url = url

        # API Keys (only set if non-empty)
        if key := self.get("llm_openai_api_key"):
            settings.llm.openai_api_key = key
        if key := self.get("llm_anthropic_api_key"):
            settings.llm.anthropic_api_key = key
        if key := self.get("llm_google_api_key"):
            settings.llm.google_api_key = key
        if key := self.get("llm_xai_api_key"):
            settings.llm.xai_api_key = key

        # General
        if name := self.get("name"):
            settings.name = name
        if wake_word := self.get("wake_word"):
            settings.wake_word = wake_word

        # Whisper
        if model := self.get("whisper_model"):
            settings.whisper.model = model
        if lang := self.get("whisper_language"):
            settings.whisper.language = lang

        # TTS
        if voice := self.get("tts_voice"):
            settings.tts.voice = voice
        if speed := self.get("tts_speed"):
            settings.tts.speed = speed

        # Vision
        if model := self.get("vision_model"):
            settings.vision.model = model
        if idx := self.get("vision_camera_index"):
            settings.vision.camera_index = idx

        # Home Assistant
        if self.get("home_assistant_enabled") is not None:
            settings.home_assistant.enabled = self.get("home_assistant_enabled")
        if url := self.get("home_assistant_url"):
            settings.home_assistant.url = url
        if token := self.get("home_assistant_token"):
            settings.home_assistant.token = token

        # MQTT
        if self.get("mqtt_enabled") is not None:
            settings.mqtt.enabled = self.get("mqtt_enabled")
        if host := self.get("mqtt_host"):
            settings.mqtt.host = host
        if port := self.get("mqtt_port"):
            settings.mqtt.port = port

        return settings


class CoreStateManager:
    """Manages WebSocket connections for the power core display."""

    def __init__(self) -> None:
        self.connections: list[WebSocket] = []
        self.current_state = "standby"

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)
        # Send current state on connect
        await websocket.send_json({"state": self.current_state})

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast_state(self, state: str) -> None:
        """Broadcast state change to all connected clients."""
        self.current_state = state
        for connection in self.connections:
            try:
                await connection.send_json({"state": state})
            except Exception:
                pass

    async def broadcast_visualizer(self, data: list[int]) -> None:
        """Broadcast visualizer data to all connected clients."""
        for connection in self.connections:
            try:
                await connection.send_json({"visualizer": data})
            except Exception:
                pass


# Global state manager for core display
core_state_manager = CoreStateManager()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application."""
    if settings is None:
        settings = Settings()

    data_dir = settings.ensure_data_dir()
    settings_manager = SettingsManager(data_dir)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager for startup/shutdown."""
        yield
        # Shutdown: clean up WebSocket connections
        for ws in core_state_manager.connections[:]:
            try:
                await ws.close()
            except Exception:
                pass
        core_state_manager.connections.clear()

    app = FastAPI(
        title="J.A.R.V.I.S. Configuration",
        description="Web UI for configuring J.A.R.V.I.S. AI assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Serve static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        """Serve the main configuration page."""
        template_path = Path(__file__).parent / "templates" / "index.html"
        if template_path.exists():
            return HTMLResponse(content=template_path.read_text())
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=500)

    @app.get("/core", response_class=HTMLResponse)
    async def core_display(request: Request) -> HTMLResponse:
        """Serve the power core visualization page."""
        template_path = Path(__file__).parent / "templates" / "core.html"
        if template_path.exists():
            return HTMLResponse(content=template_path.read_text())
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=500)

    @app.websocket("/ws/core")
    async def core_websocket(websocket: WebSocket) -> None:
        """WebSocket endpoint for power core state updates."""
        await core_state_manager.connect(websocket)
        try:
            while True:
                # Keep connection alive and listen for client messages
                data = await websocket.receive_text()
                # Client can send state updates (e.g., from voice activity)
                try:
                    msg = json.loads(data)
                    if "state" in msg:
                        await core_state_manager.broadcast_state(msg["state"])
                except json.JSONDecodeError:
                    pass
        except (WebSocketDisconnect, RuntimeError):
            # RuntimeError can occur if WebSocket disconnects between accept and receive
            core_state_manager.disconnect(websocket)

    @app.get("/api/settings")
    async def get_settings() -> dict[str, Any]:
        """Get current settings."""
        stored = settings_manager.get_all()

        # Merge with defaults, masking sensitive values
        result = {
            # General
            "name": stored.get("name", settings.name),
            "wake_word": stored.get("wake_word", settings.wake_word),
            # LLM
            "llm_provider": stored.get("llm_provider", settings.llm.provider.value),
            "llm_model": stored.get("llm_model", settings.llm.model),
            "llm_temperature": stored.get("llm_temperature", settings.llm.temperature),
            "llm_max_tokens": stored.get("llm_max_tokens", settings.llm.max_tokens),
            "llm_ollama_base_url": stored.get("llm_ollama_base_url", settings.llm.ollama_base_url),
            # API keys - mask for display
            "llm_openai_api_key_set": bool(stored.get("llm_openai_api_key") or settings.llm.openai_api_key),
            "llm_anthropic_api_key_set": bool(stored.get("llm_anthropic_api_key") or settings.llm.anthropic_api_key),
            "llm_google_api_key_set": bool(stored.get("llm_google_api_key") or settings.llm.google_api_key),
            "llm_xai_api_key_set": bool(stored.get("llm_xai_api_key") or settings.llm.xai_api_key),
            # Whisper
            "whisper_model": stored.get("whisper_model", settings.whisper.model),
            "whisper_language": stored.get("whisper_language", settings.whisper.language),
            # TTS
            "tts_voice": stored.get("tts_voice", settings.tts.voice),
            "tts_speed": stored.get("tts_speed", settings.tts.speed),
            # Vision
            "vision_model": stored.get("vision_model", settings.vision.model),
            "vision_camera_index": stored.get("vision_camera_index", settings.vision.camera_index),
            # Home Assistant
            "home_assistant_enabled": stored.get("home_assistant_enabled", settings.home_assistant.enabled),
            "home_assistant_url": stored.get("home_assistant_url", settings.home_assistant.url),
            "home_assistant_token_set": bool(stored.get("home_assistant_token") or settings.home_assistant.token),
            # MQTT
            "mqtt_enabled": stored.get("mqtt_enabled", settings.mqtt.enabled),
            "mqtt_host": stored.get("mqtt_host", settings.mqtt.host),
            "mqtt_port": stored.get("mqtt_port", settings.mqtt.port),
            # Skills
            "default_location": stored.get("default_location", "New York"),
        }
        return result

    @app.post("/api/settings")
    async def update_settings(updates: SettingsUpdate) -> dict[str, str]:
        """Update settings."""
        update_dict = updates.model_dump(exclude_none=True)
        settings_manager.update(update_dict)
        return {"status": "ok", "message": "Settings updated"}

    @app.get("/api/providers")
    async def get_providers() -> dict[str, Any]:
        """Get available LLM providers and their models."""
        return {
            "providers": [
                {
                    "id": "ollama",
                    "name": "Ollama (Local)",
                    "models": ["llama3.2", "llama3.1", "mistral", "codellama", "phi3"],
                },
                {
                    "id": "openai",
                    "name": "OpenAI",
                    "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                },
                {
                    "id": "anthropic",
                    "name": "Anthropic (Claude)",
                    "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
                },
                {
                    "id": "google",
                    "name": "Google (Gemini)",
                    "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
                },
                {
                    "id": "xai",
                    "name": "xAI (Grok)",
                    "models": ["grok-2-latest", "grok-beta"],
                },
            ]
        }

    @app.get("/api/status")
    async def get_status() -> dict[str, Any]:
        """Get system status."""
        import platform

        return {
            "status": "running",
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "settings_loaded": True,
        }

    @app.post("/api/test-connection")
    async def test_connection(data: dict[str, str]) -> dict[str, Any]:
        """Test connection to a service."""
        service = data.get("service")

        if service == "ollama":
            import httpx

            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    url = data.get("url", "http://localhost:11434")
                    response = await client.get(f"{url}/api/tags")
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        return {
                            "success": True,
                            "message": f"Connected! Found {len(models)} models.",
                            "models": [m["name"] for m in models],
                        }
            except Exception as e:
                return {"success": False, "message": str(e)}

        elif service == "home_assistant":
            import httpx

            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    url = data.get("url", "")
                    token = data.get("token", "")
                    response = await client.get(
                        f"{url}/api/",
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    if response.status_code == 200:
                        return {"success": True, "message": "Connected to Home Assistant!"}
                    return {"success": False, "message": f"HTTP {response.status_code}"}
            except Exception as e:
                return {"success": False, "message": str(e)}

        return {"success": False, "message": "Unknown service"}

    return app


def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Run the web server."""
    import signal
    import sys

    import uvicorn

    app = create_app()

    config = uvicorn.Config(app, host=host, port=port, loop="asyncio")
    server = uvicorn.Server(config)

    def signal_handler(signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        print("\nShutting down...")
        server.should_exit = True
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server.run()


if __name__ == "__main__":
    run_server()
