"""Home automation integration with Home Assistant and MQTT."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import aiohttp

from core.config import HomeAssistantSettings, MQTTSettings


class DeviceType(Enum):
    """Types of smart home devices."""

    LIGHT = auto()
    SWITCH = auto()
    LOCK = auto()
    THERMOSTAT = auto()
    SENSOR = auto()
    MEDIA_PLAYER = auto()
    COVER = auto()  # Blinds, garage doors
    FAN = auto()
    CAMERA = auto()
    VACUUM = auto()
    SCENE = auto()
    AUTOMATION = auto()
    SCRIPT = auto()
    UNKNOWN = auto()


@dataclass
class Device:
    """A smart home device."""

    entity_id: str
    name: str
    device_type: DeviceType
    state: str
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def domain(self) -> str:
        """Get the domain (first part of entity_id)."""
        return self.entity_id.split(".")[0]

    @property
    def is_on(self) -> bool:
        """Check if device is on."""
        return self.state in ("on", "playing", "open", "unlocked", "home")

    @property
    def is_available(self) -> bool:
        """Check if device is available."""
        return self.state != "unavailable"


@dataclass
class Scene:
    """A Home Assistant scene."""

    entity_id: str
    name: str


@dataclass
class Area:
    """A Home Assistant area/room."""

    area_id: str
    name: str
    devices: list[Device] = field(default_factory=list)


class HomeAutomation:
    """Interface to smart home devices via Home Assistant and MQTT.

    Supports:
    - Home Assistant REST API for device control
    - Scenes and automations
    - Climate/thermostat control
    - Media player control
    - Device discovery and area management
    - MQTT for direct device communication
    """

    def __init__(
        self,
        ha_settings: HomeAssistantSettings,
        mqtt_settings: MQTTSettings,
    ) -> None:
        self.ha_settings = ha_settings
        self.mqtt_settings = mqtt_settings
        self._session: aiohttp.ClientSession | None = None
        self._mqtt_client: Any = None
        self._devices: dict[str, Device] = {}
        self._scenes: dict[str, Scene] = {}
        self._areas: dict[str, Area] = {}
        self._last_refresh: float = 0

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self.ha_settings.token}",
                "Content-Type": "application/json",
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def _ha_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Make a request to Home Assistant API."""
        session = await self._get_session()
        url = f"{self.ha_settings.url}/api/{endpoint}"

        async with session.request(method, url, json=data) as response:
            response.raise_for_status()
            return await response.json()

    async def connect_mqtt(self) -> None:
        """Connect to MQTT broker."""
        if not self.mqtt_settings.enabled:
            return

        import aiomqtt

        self._mqtt_client = aiomqtt.Client(
            hostname=self.mqtt_settings.host,
            port=self.mqtt_settings.port,
            username=self.mqtt_settings.username or None,
            password=self.mqtt_settings.password or None,
        )
        await self._mqtt_client.__aenter__()

    async def refresh_devices(self) -> list[Device]:
        """Fetch all devices from Home Assistant."""
        import time

        states = await self._ha_request("GET", "states")

        self._devices.clear()
        self._scenes.clear()

        domain_mapping = {
            "light": DeviceType.LIGHT,
            "switch": DeviceType.SWITCH,
            "lock": DeviceType.LOCK,
            "climate": DeviceType.THERMOSTAT,
            "sensor": DeviceType.SENSOR,
            "binary_sensor": DeviceType.SENSOR,
            "media_player": DeviceType.MEDIA_PLAYER,
            "cover": DeviceType.COVER,
            "fan": DeviceType.FAN,
            "camera": DeviceType.CAMERA,
            "vacuum": DeviceType.VACUUM,
            "scene": DeviceType.SCENE,
            "automation": DeviceType.AUTOMATION,
            "script": DeviceType.SCRIPT,
        }

        for state in states:
            entity_id = state["entity_id"]
            domain = entity_id.split(".")[0]
            device_type = domain_mapping.get(domain, DeviceType.UNKNOWN)

            # Skip internal entities
            if entity_id.startswith(("persistent_notification.", "zone.")):
                continue

            device = Device(
                entity_id=entity_id,
                name=state["attributes"].get("friendly_name", entity_id),
                device_type=device_type,
                state=state["state"],
                attributes=state["attributes"],
            )
            self._devices[entity_id] = device

            # Track scenes separately
            if device_type == DeviceType.SCENE:
                self._scenes[entity_id] = Scene(
                    entity_id=entity_id,
                    name=device.name,
                )

        self._last_refresh = time.time()
        return list(self._devices.values())

    async def get_device(self, name_or_id: str) -> Device | None:
        """Find a device by name or entity_id."""
        # Direct match
        if name_or_id in self._devices:
            return self._devices[name_or_id]

        # Search by friendly name (fuzzy)
        name_lower = name_or_id.lower()
        best_match: Device | None = None
        best_score = 0

        for device in self._devices.values():
            device_name_lower = device.name.lower()

            # Exact match
            if name_lower == device_name_lower:
                return device

            # Partial match
            if name_lower in device_name_lower:
                score = len(name_lower) / len(device_name_lower)
                if score > best_score:
                    best_score = score
                    best_match = device

            # Words match
            name_words = set(name_lower.split())
            device_words = set(device_name_lower.split())
            if name_words & device_words:
                score = len(name_words & device_words) / len(name_words)
                if score > best_score:
                    best_score = score
                    best_match = device

        return best_match

    async def get_devices_by_type(self, device_type: DeviceType) -> list[Device]:
        """Get all devices of a specific type."""
        return [d for d in self._devices.values() if d.device_type == device_type]

    async def get_devices_by_area(self, area_name: str) -> list[Device]:
        """Get all devices in an area/room."""
        area_lower = area_name.lower()
        return [
            d for d in self._devices.values()
            if area_lower in d.name.lower() or area_lower in d.entity_id.lower()
        ]

    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Call a Home Assistant service."""
        data = {**kwargs}
        if entity_id:
            data["entity_id"] = entity_id
        await self._ha_request("POST", f"services/{domain}/{service}", data)

    # === Light Controls ===

    async def turn_on(self, device: Device | str, **kwargs: Any) -> None:
        """Turn on a device."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service(device.domain, "turn_on", device.entity_id, **kwargs)

    async def turn_off(self, device: Device | str) -> None:
        """Turn off a device."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service(device.domain, "turn_off", device.entity_id)

    async def toggle(self, device: Device | str) -> None:
        """Toggle a device."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service(device.domain, "toggle", device.entity_id)

    async def set_brightness(self, device: Device | str, brightness: int) -> None:
        """Set light brightness (0-100)."""
        brightness_255 = int(brightness * 255 / 100)
        await self.turn_on(device, brightness=brightness_255)

    async def set_color(
        self, device: Device | str, color: tuple[int, int, int] | str
    ) -> None:
        """Set light color (RGB tuple or color name)."""
        if isinstance(color, str):
            # Named colors
            color_map = {
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "yellow": (255, 255, 0),
                "purple": (128, 0, 128),
                "orange": (255, 165, 0),
                "pink": (255, 192, 203),
                "white": (255, 255, 255),
                "warm": (255, 180, 100),
                "cool": (200, 220, 255),
            }
            color = color_map.get(color.lower(), (255, 255, 255))

        await self.turn_on(device, rgb_color=list(color))

    # === Lock Controls ===

    async def lock(self, device: Device | str) -> None:
        """Lock a lock."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("lock", "lock", device.entity_id)

    async def unlock(self, device: Device | str) -> None:
        """Unlock a lock."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("lock", "unlock", device.entity_id)

    # === Climate/Thermostat Controls ===

    async def set_temperature(
        self,
        device: Device | str,
        temperature: float,
        target_temp_high: float | None = None,
        target_temp_low: float | None = None,
    ) -> None:
        """Set thermostat temperature."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        data: dict[str, Any] = {"temperature": temperature}
        if target_temp_high is not None:
            data["target_temp_high"] = target_temp_high
        if target_temp_low is not None:
            data["target_temp_low"] = target_temp_low

        await self.call_service("climate", "set_temperature", device.entity_id, **data)

    async def set_hvac_mode(self, device: Device | str, mode: str) -> None:
        """Set HVAC mode (heat, cool, auto, off)."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("climate", "set_hvac_mode", device.entity_id, hvac_mode=mode)

    async def get_temperature(self, device: Device | str) -> dict[str, Any]:
        """Get current thermostat state."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        return {
            "current_temperature": device.attributes.get("current_temperature"),
            "target_temperature": device.attributes.get("temperature"),
            "hvac_mode": device.state,
            "hvac_action": device.attributes.get("hvac_action"),
        }

    # === Media Player Controls ===

    async def media_play(self, device: Device | str) -> None:
        """Play media."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("media_player", "media_play", device.entity_id)

    async def media_pause(self, device: Device | str) -> None:
        """Pause media."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("media_player", "media_pause", device.entity_id)

    async def media_stop(self, device: Device | str) -> None:
        """Stop media."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("media_player", "media_stop", device.entity_id)

    async def media_next(self, device: Device | str) -> None:
        """Skip to next track."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("media_player", "media_next_track", device.entity_id)

    async def media_previous(self, device: Device | str) -> None:
        """Go to previous track."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("media_player", "media_previous_track", device.entity_id)

    async def set_volume(self, device: Device | str, volume: float) -> None:
        """Set volume (0-100)."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service(
            "media_player", "volume_set", device.entity_id, volume_level=volume / 100
        )

    # === Cover Controls (blinds, garage doors) ===

    async def open_cover(self, device: Device | str) -> None:
        """Open a cover (blinds, garage door)."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("cover", "open_cover", device.entity_id)

    async def close_cover(self, device: Device | str) -> None:
        """Close a cover."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("cover", "close_cover", device.entity_id)

    async def set_cover_position(self, device: Device | str, position: int) -> None:
        """Set cover position (0-100)."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("cover", "set_cover_position", device.entity_id, position=position)

    # === Scenes and Automations ===

    async def activate_scene(self, scene: str) -> None:
        """Activate a scene by name or entity_id."""
        # Try direct entity_id first
        if scene.startswith("scene."):
            await self.call_service("scene", "turn_on", scene)
            return

        # Search by name
        scene_lower = scene.lower()
        for s in self._scenes.values():
            if scene_lower in s.name.lower():
                await self.call_service("scene", "turn_on", s.entity_id)
                return

        raise ValueError(f"Scene not found: {scene}")

    async def list_scenes(self) -> list[Scene]:
        """Get all available scenes."""
        return list(self._scenes.values())

    async def trigger_automation(self, automation: str) -> None:
        """Trigger an automation."""
        device = await self.get_device(automation)
        if not device or device.device_type != DeviceType.AUTOMATION:
            raise ValueError(f"Automation not found: {automation}")

        await self.call_service("automation", "trigger", device.entity_id)

    async def run_script(self, script: str) -> None:
        """Run a script."""
        if not script.startswith("script."):
            script = f"script.{script}"

        await self.call_service("script", "turn_on", script)

    # === Vacuum Controls ===

    async def vacuum_start(self, device: Device | str) -> None:
        """Start vacuum."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("vacuum", "start", device.entity_id)

    async def vacuum_stop(self, device: Device | str) -> None:
        """Stop vacuum."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("vacuum", "stop", device.entity_id)

    async def vacuum_return_home(self, device: Device | str) -> None:
        """Send vacuum home."""
        if isinstance(device, str):
            found = await self.get_device(device)
            if not found:
                raise ValueError(f"Device not found: {device}")
            device = found

        await self.call_service("vacuum", "return_to_base", device.entity_id)

    # === MQTT ===

    async def publish_mqtt(self, topic: str, payload: str) -> None:
        """Publish a message to MQTT topic."""
        if self._mqtt_client:
            await self._mqtt_client.publish(topic, payload)

    async def subscribe_mqtt(self, topic: str) -> Any:
        """Subscribe to MQTT topic."""
        if self._mqtt_client:
            await self._mqtt_client.subscribe(topic)
            return self._mqtt_client.messages
        return None

    # === Utilities ===

    async def get_state_summary(self) -> dict[str, Any]:
        """Get a summary of all device states."""
        lights_on = sum(1 for d in self._devices.values() if d.device_type == DeviceType.LIGHT and d.is_on)
        total_lights = sum(1 for d in self._devices.values() if d.device_type == DeviceType.LIGHT)

        locks_locked = sum(1 for d in self._devices.values() if d.device_type == DeviceType.LOCK and d.state == "locked")
        total_locks = sum(1 for d in self._devices.values() if d.device_type == DeviceType.LOCK)

        # Get thermostat info
        thermostats = await self.get_devices_by_type(DeviceType.THERMOSTAT)
        thermostat_info = None
        if thermostats:
            t = thermostats[0]
            thermostat_info = {
                "current": t.attributes.get("current_temperature"),
                "target": t.attributes.get("temperature"),
                "mode": t.state,
            }

        return {
            "lights": {"on": lights_on, "total": total_lights},
            "locks": {"locked": locks_locked, "total": total_locks},
            "thermostat": thermostat_info,
            "total_devices": len(self._devices),
        }

    async def close(self) -> None:
        """Cleanup connections."""
        if self._session:
            await self._session.close()
            self._session = None

        if self._mqtt_client:
            await self._mqtt_client.__aexit__(None, None, None)
            self._mqtt_client = None
