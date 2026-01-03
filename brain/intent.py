"""Intent parsing and command extraction."""

import re
from dataclasses import dataclass, field
from enum import Enum, auto


class IntentType(Enum):
    """Types of user intents."""

    CONVERSATION = auto()  # General chat
    HOME_CONTROL = auto()  # Smart home commands
    INFORMATION = auto()  # Questions, lookups
    SYSTEM = auto()  # System commands (volume, etc.)
    VISION = auto()  # Camera/vision requests
    UNKNOWN = auto()


@dataclass
class Intent:
    """Parsed intent from user input."""

    type: IntentType
    action: str | None = None
    target: str | None = None
    parameters: dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0
    raw_text: str = ""


class IntentParser:
    """Parses user input to extract structured intents.

    Uses pattern matching for common commands before falling back to LLM.
    This provides fast response for simple commands.
    """

    # Pattern-based intent matching for speed
    HOME_PATTERNS = [
        (r"turn (on|off) (?:the )?(.+)", "power", ["state", "device"]),
        (r"set (?:the )?(.+) to (\d+)%?", "set_level", ["device", "level"]),
        (r"dim (?:the )?(.+)", "dim", ["device"]),
        (r"brighten (?:the )?(.+)", "brighten", ["device"]),
        (r"(lock|unlock) (?:the )?(.+)", "lock", ["action", "device"]),
    ]

    SYSTEM_PATTERNS = [
        (r"set volume to (\d+)%?", "volume", ["level"]),
        (r"(mute|unmute)", "mute", ["action"]),
        (r"(pause|play|stop|next|previous)", "media", ["action"]),
    ]

    VISION_PATTERNS = [
        (r"what do you see", "describe", []),
        (r"who is (?:that|there)", "identify", []),
        (r"is (?:there )?anyone (?:there|here)", "detect_people", []),
    ]

    def parse(self, text: str) -> Intent:
        """Parse text into an Intent.

        First tries pattern matching for speed, then falls back to
        indicating CONVERSATION intent for LLM handling.
        """
        text_lower = text.lower().strip()

        # Try home automation patterns
        for pattern, action, param_names in self.HOME_PATTERNS:
            if match := re.search(pattern, text_lower):
                params = dict(zip(param_names, match.groups()))
                return Intent(
                    type=IntentType.HOME_CONTROL,
                    action=action,
                    target=params.get("device"),
                    parameters=params,
                    raw_text=text,
                )

        # Try system patterns
        for pattern, action, param_names in self.SYSTEM_PATTERNS:
            if match := re.search(pattern, text_lower):
                params = dict(zip(param_names, match.groups()))
                return Intent(
                    type=IntentType.SYSTEM,
                    action=action,
                    parameters=params,
                    raw_text=text,
                )

        # Try vision patterns
        for pattern, action, param_names in self.VISION_PATTERNS:
            if match := re.search(pattern, text_lower):
                params = dict(zip(param_names, match.groups()))
                return Intent(
                    type=IntentType.VISION,
                    action=action,
                    parameters=params,
                    raw_text=text,
                )

        # Default to conversation - let LLM handle it
        return Intent(
            type=IntentType.CONVERSATION,
            raw_text=text,
        )

    def is_question(self, text: str) -> bool:
        """Check if text is a question."""
        question_words = ["what", "who", "where", "when", "why", "how", "is", "are", "can", "do"]
        text_lower = text.lower().strip()
        return text_lower.endswith("?") or any(text_lower.startswith(w) for w in question_words)
