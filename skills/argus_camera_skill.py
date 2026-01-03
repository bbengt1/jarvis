"""ArgusAI Camera Skill - AI-powered home security camera integration."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import httpx

from skills.base import Skill, SkillResult

if TYPE_CHECKING:
    from core.context import ConversationContext
    from core.jarvis import Jarvis


@dataclass
class Camera:
    """Camera representation."""

    id: str
    name: str
    source_type: str
    is_active: bool
    status: str


@dataclass
class Event:
    """Security event representation."""

    id: str
    camera_id: str
    camera_name: str
    timestamp: datetime
    description: str
    entities: list[str]
    confidence: float


class ArgusCameraSkill(Skill):
    """Integrates with ArgusAI for AI-powered security camera monitoring.

    ArgusAI provides real-time event detection and analysis using multiple
    AI providers (GPT-4, Claude, Gemini, Grok) for home security cameras.
    """

    name = "argus_camera"
    description = "AI-powered security camera monitoring and event detection"
    triggers = [
        "camera",
        "cameras",
        "security",
        "motion",
        "surveillance",
        "recording",
        "driveway",
        "front door",
        "back door",
        "backyard",
        "garage",
        "porch",
        "outside",
        "visitor",
        "package",
        "delivery",
        "someone",
        "anyone",
        "intruder",
    ]

    def __init__(self, jarvis: "Jarvis") -> None:
        super().__init__(jarvis)
        # Keywords that suggest camera/security context
        self._context_keywords = [
            "camera", "cameras", "security", "motion", "movement", "activity",
            "surveillance", "recording", "monitoring", "watching", "detect",
            "event", "events", "alert", "alerts", "notification",
        ]
        # Location keywords that often refer to cameras
        self._location_keywords = [
            "driveway", "front door", "back door", "backyard", "front yard",
            "garage", "porch", "patio", "entrance", "gate", "sidewalk",
            "street", "yard", "garden", "pool", "basement", "attic",
        ]
        # Action keywords
        self._check_keywords = [
            "check", "look", "see", "show", "happening", "going on",
            "anyone", "someone", "anything", "visitor", "package",
            "delivery", "car", "person", "people", "animal", "dog", "cat",
        ]
        self._control_keywords = [
            "start", "stop", "enable", "disable", "turn on", "turn off",
            "activate", "deactivate", "pause", "resume",
        ]

        settings = jarvis.settings.argus_ai
        self._base_url = settings.base_url.rstrip("/")
        self._api_key = settings.api_key
        self._enabled = settings.enabled
        self._client = httpx.AsyncClient(
            timeout=15.0,
            headers={"X-API-Key": self._api_key} if self._api_key else {},
        )

    async def can_handle(self, text: str, context: "ConversationContext") -> bool:
        """Check if this is a camera-related request using natural language understanding."""
        if not self._enabled:
            return False

        text_lower = text.lower()

        # Direct camera/security mentions
        if any(kw in text_lower for kw in self._context_keywords):
            return True

        # Location + check action (e.g., "is anyone at the front door?")
        has_location = any(loc in text_lower for loc in self._location_keywords)
        has_check = any(kw in text_lower for kw in self._check_keywords)
        if has_location and has_check:
            return True

        # Location + control action (e.g., "turn on the garage camera")
        has_control = any(kw in text_lower for kw in self._control_keywords)
        if has_location and has_control:
            return True

        # Questions about what's happening outside/at locations
        if has_location and any(q in text_lower for q in ["what", "who", "is there", "any"]):
            return True

        return False

    async def _api_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any] | list[Any] | None:
        """Make an API request to ArgusAI."""
        try:
            url = f"{self._base_url}{endpoint}"
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception:
            return None

    async def _get_cameras(self) -> list[Camera]:
        """Fetch all cameras."""
        data = await self._api_request("GET", "/cameras")
        if not data:
            return []

        cameras = []
        for cam in data if isinstance(data, list) else data.get("cameras", []):
            cameras.append(
                Camera(
                    id=cam.get("id", ""),
                    name=cam.get("name", "Unknown"),
                    source_type=cam.get("source_type", "unknown"),
                    is_active=cam.get("is_active", False),
                    status=cam.get("status", "unknown"),
                )
            )
        return cameras

    async def _get_camera_by_name(self, name: str) -> Camera | None:
        """Find a camera by name (fuzzy match)."""
        cameras = await self._get_cameras()
        name_lower = name.lower().strip()

        # Exact match first
        for cam in cameras:
            if cam.name.lower() == name_lower:
                return cam

        # Partial match
        for cam in cameras:
            if name_lower in cam.name.lower() or cam.name.lower() in name_lower:
                return cam

        return None

    async def _get_events(
        self, camera_id: str | None = None, limit: int = 5
    ) -> list[Event]:
        """Fetch recent events."""
        params: dict[str, Any] = {"limit": limit}
        if camera_id:
            params["camera_id"] = camera_id

        data = await self._api_request("GET", "/events", params=params)
        if not data:
            return []

        events = []
        event_list = data if isinstance(data, list) else data.get("events", [])
        for evt in event_list:
            try:
                timestamp = datetime.fromisoformat(
                    evt.get("timestamp", "").replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                timestamp = datetime.now()

            events.append(
                Event(
                    id=evt.get("id", ""),
                    camera_id=evt.get("camera_id", ""),
                    camera_name=evt.get("camera_name", "Unknown"),
                    timestamp=timestamp,
                    description=evt.get("description", "No description"),
                    entities=evt.get("entities", []),
                    confidence=evt.get("confidence", 0.0),
                )
            )
        return events

    async def _start_camera(self, camera_id: str) -> bool:
        """Start a camera."""
        result = await self._api_request("POST", f"/cameras/{camera_id}/start")
        return result is not None

    async def _stop_camera(self, camera_id: str) -> bool:
        """Stop a camera."""
        result = await self._api_request("POST", f"/cameras/{camera_id}/stop")
        return result is not None

    async def _reanalyze_event(self, event_id: str) -> dict[str, Any] | None:
        """Re-analyze an event with AI."""
        return await self._api_request("POST", f"/events/{event_id}/reanalyze")

    async def _check_health(self) -> bool:
        """Check if ArgusAI is healthy."""
        result = await self._api_request("GET", "/health")
        return result is not None and result.get("status") == "healthy"

    def _format_time_ago(self, dt: datetime) -> str:
        """Format a datetime as time ago."""
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

    def _extract_location(self, text: str) -> str | None:
        """Extract a location/camera name from natural language."""
        text_lower = text.lower()

        # Check for explicit camera mentions like "the driveway camera"
        for loc in self._location_keywords:
            if loc in text_lower:
                return loc

        # Try to find camera name patterns
        patterns = [
            r"(?:the |my )?(\w+(?:\s+\w+)?)\s+camera",
            r"camera\s+(?:at|on|in|for)\s+(?:the\s+)?(\w+(?:\s+\w+)?)",
            r"(?:at|on|in)\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s*\??$",
        ]
        for pattern in patterns:
            if match := re.search(pattern, text_lower):
                return match.group(1).strip()

        return None

    def _detect_intent(self, text: str) -> tuple[str, str | None]:
        """Detect the user's intent from natural language.

        Returns:
            Tuple of (intent, location/camera_name or None)
        """
        text_lower = text.lower()
        location = self._extract_location(text)

        # Control intents - start/stop cameras
        start_phrases = ["start", "turn on", "enable", "activate", "begin monitoring", "watch"]
        stop_phrases = ["stop", "turn off", "disable", "deactivate", "stop monitoring", "pause"]

        if any(phrase in text_lower for phrase in start_phrases):
            return ("start_camera", location)
        if any(phrase in text_lower for phrase in stop_phrases):
            return ("stop_camera", location)

        # Re-analyze intent
        if any(kw in text_lower for kw in ["reanalyze", "re-analyze", "analyze again", "look again"]):
            return ("reanalyze", None)

        # List cameras intent
        list_phrases = ["how many cameras", "list cameras", "show cameras", "what cameras", "which cameras", "all cameras", "my cameras"]
        if any(phrase in text_lower for phrase in list_phrases):
            return ("list_cameras", None)

        # Status intent
        if "status" in text_lower or "security status" in text_lower:
            return ("status", None)

        # Check specific location - questions about what's happening
        check_phrases = [
            "anyone", "someone", "anything", "something",
            "what's happening", "what is happening", "going on",
            "check", "look at", "show me", "see",
            "who's at", "who is at", "is there",
            "any activity", "any motion", "any movement",
            "visitor", "package", "delivery", "car",
        ]
        if location and any(phrase in text_lower for phrase in check_phrases):
            return ("check_location", location)

        # General event queries
        event_phrases = [
            "any events", "recent events", "what happened", "what did you see",
            "any alerts", "notifications", "detected anything", "motion detected",
            "any activity", "anything unusual", "anything suspicious",
        ]
        if any(phrase in text_lower for phrase in event_phrases):
            return ("recent_events", None)

        # If we have a location mentioned, default to checking it
        if location:
            return ("check_location", location)

        # Default to status overview
        return ("status", None)

    async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
        """Execute camera-related requests using natural language understanding."""
        if not self._enabled:
            return SkillResult(
                success=False,
                response="ArgusAI camera integration is not enabled. Please configure it in settings.",
            )

        if not self._api_key:
            return SkillResult(
                success=False,
                response="ArgusAI API key is not configured. Please add your API key in settings.",
            )

        # Check ArgusAI connectivity
        if not await self._check_health():
            return SkillResult(
                success=False,
                response="I can't connect to ArgusAI right now. Please check that the service is running.",
            )

        # Detect intent from natural language
        intent, location = self._detect_intent(text)

        match intent:
            case "list_cameras":
                return await self._handle_list_cameras()
            case "status":
                return await self._handle_status()
            case "start_camera":
                if location:
                    return await self._handle_start_camera(location)
                return SkillResult(
                    success=False,
                    response="Which camera would you like me to start?",
                )
            case "stop_camera":
                if location:
                    return await self._handle_stop_camera(location)
                return SkillResult(
                    success=False,
                    response="Which camera would you like me to stop?",
                )
            case "reanalyze":
                return await self._handle_reanalyze()
            case "check_location":
                if location:
                    return await self._handle_camera_events(location)
                return await self._handle_recent_events()
            case "recent_events":
                return await self._handle_recent_events()
            case _:
                return await self._handle_status()

    async def _handle_list_cameras(self) -> SkillResult:
        """List all cameras."""
        cameras = await self._get_cameras()

        if not cameras:
            return SkillResult(
                success=True,
                response="No cameras are configured in ArgusAI.",
                data={"cameras": []},
            )

        active = [c for c in cameras if c.is_active]
        inactive = [c for c in cameras if not c.is_active]

        response = f"You have {len(cameras)} camera{'s' if len(cameras) != 1 else ''}. "
        if active:
            names = ", ".join(c.name for c in active)
            response += f"{len(active)} active: {names}. "
        if inactive:
            names = ", ".join(c.name for c in inactive)
            response += f"{len(inactive)} inactive: {names}."

        return SkillResult(
            success=True,
            response=response.strip(),
            data={"cameras": [vars(c) for c in cameras]},
        )

    async def _handle_status(self) -> SkillResult:
        """Get overall security status."""
        cameras = await self._get_cameras()
        events = await self._get_events(limit=3)

        active_count = sum(1 for c in cameras if c.is_active)
        response = f"Security status: {active_count} of {len(cameras)} cameras active. "

        if events:
            latest = events[0]
            time_ago = self._format_time_ago(latest.timestamp)
            response += f"Latest event {time_ago} on {latest.camera_name}: {latest.description}"
        else:
            response += "No recent events detected."

        return SkillResult(
            success=True,
            response=response,
            data={
                "cameras": [vars(c) for c in cameras],
                "recent_events": [vars(e) for e in events],
            },
        )

    async def _handle_start_camera(self, camera_name: str) -> SkillResult:
        """Start a specific camera."""
        camera = await self._get_camera_by_name(camera_name)
        if not camera:
            return SkillResult(
                success=False,
                response=f"I couldn't find a camera named '{camera_name}'.",
            )

        if camera.is_active:
            return SkillResult(
                success=True,
                response=f"The {camera.name} camera is already running.",
            )

        if await self._start_camera(camera.id):
            return SkillResult(
                success=True,
                response=f"Started the {camera.name} camera. It's now monitoring.",
            )
        else:
            return SkillResult(
                success=False,
                response=f"Failed to start the {camera.name} camera. Please check ArgusAI logs.",
            )

    async def _handle_stop_camera(self, camera_name: str) -> SkillResult:
        """Stop a specific camera."""
        camera = await self._get_camera_by_name(camera_name)
        if not camera:
            return SkillResult(
                success=False,
                response=f"I couldn't find a camera named '{camera_name}'.",
            )

        if not camera.is_active:
            return SkillResult(
                success=True,
                response=f"The {camera.name} camera is already stopped.",
            )

        if await self._stop_camera(camera.id):
            return SkillResult(
                success=True,
                response=f"Stopped the {camera.name} camera.",
            )
        else:
            return SkillResult(
                success=False,
                response=f"Failed to stop the {camera.name} camera. Please check ArgusAI logs.",
            )

    async def _handle_camera_events(self, camera_name: str) -> SkillResult:
        """Get events for a specific camera."""
        camera = await self._get_camera_by_name(camera_name)
        if not camera:
            return SkillResult(
                success=False,
                response=f"I couldn't find a camera named '{camera_name}'.",
            )

        events = await self._get_events(camera_id=camera.id, limit=5)

        if not events:
            status = "actively monitoring" if camera.is_active else "currently inactive"
            return SkillResult(
                success=True,
                response=f"No recent events on the {camera.name} camera. It's {status}.",
                data={"camera": vars(camera), "events": []},
            )

        response = f"Recent events on {camera.name}: "
        for evt in events[:3]:
            time_ago = self._format_time_ago(evt.timestamp)
            response += f"{time_ago}: {evt.description}. "

        return SkillResult(
            success=True,
            response=response.strip(),
            data={"camera": vars(camera), "events": [vars(e) for e in events]},
        )

    async def _handle_recent_events(self) -> SkillResult:
        """Get recent events across all cameras."""
        events = await self._get_events(limit=5)

        if not events:
            return SkillResult(
                success=True,
                response="No recent security events detected across your cameras.",
                data={"events": []},
            )

        response = "Recent security events: "
        for evt in events[:3]:
            time_ago = self._format_time_ago(evt.timestamp)
            response += f"{evt.camera_name} ({time_ago}): {evt.description}. "

        if len(events) > 3:
            response += f"Plus {len(events) - 3} more event{'s' if len(events) - 3 != 1 else ''}."

        return SkillResult(
            success=True,
            response=response.strip(),
            data={"events": [vars(e) for e in events]},
        )

    async def _handle_reanalyze(self) -> SkillResult:
        """Re-analyze the most recent event."""
        events = await self._get_events(limit=1)

        if not events:
            return SkillResult(
                success=False,
                response="There are no recent events to re-analyze.",
            )

        event = events[0]
        result = await self._reanalyze_event(event.id)

        if result:
            new_description = result.get("description", event.description)
            return SkillResult(
                success=True,
                response=f"Re-analyzed the last event from {event.camera_name}. New analysis: {new_description}",
                data={"event": vars(event), "new_analysis": result},
            )
        else:
            return SkillResult(
                success=False,
                response="Failed to re-analyze the event. The AI service may be unavailable.",
            )

    async def close(self) -> None:
        """Cleanup."""
        await self._client.aclose()
