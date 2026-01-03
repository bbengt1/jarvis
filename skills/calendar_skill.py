"""Calendar skill - manages calendar events."""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from skills.base import Skill, SkillResult

if TYPE_CHECKING:
    from core.context import ConversationContext
    from core.jarvis import Jarvis


@dataclass
class CalendarEvent:
    """A calendar event."""

    id: str
    title: str
    start: datetime
    end: datetime | None = None
    location: str = ""
    description: str = ""
    all_day: bool = False
    recurring: str = ""  # daily, weekly, monthly, yearly, or empty

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["start"] = self.start.isoformat()
        data["end"] = self.end.isoformat() if self.end else None
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "CalendarEvent":
        """Create from dictionary."""
        data["start"] = datetime.fromisoformat(data["start"])
        if data.get("end"):
            data["end"] = datetime.fromisoformat(data["end"])
        return cls(**data)


class CalendarSkill(Skill):
    """Manages calendar events with local storage.

    Supports creating, listing, and managing events.
    Can integrate with external calendars via ICS import.
    """

    name = "calendar"
    description = "Manages calendar events and schedules"
    triggers = ["calendar", "schedule", "event", "meeting", "appointment", "agenda"]

    def __init__(self, jarvis: "Jarvis") -> None:
        super().__init__(jarvis)
        self._patterns = [
            r"(?:what(?:'s| is) )?(?:on )?my (?:calendar|schedule|agenda)",
            r"(?:what )?(?:do i have|am i doing) (?:today|tomorrow|this week)",
            r"(?:add|create|schedule|set up) (?:a |an )?(?:event|meeting|appointment)",
            r"(?:remind me about|what(?:'s| is) happening)",
            r"(?:cancel|delete|remove) (?:the |my )?(?:event|meeting|appointment)",
            r"(?:when is|what time is) (?:the |my )?",
        ]
        self._events: list[CalendarEvent] = []
        self._storage_path: Path | None = None
        self._loaded = False

    def _ensure_storage(self) -> Path:
        """Ensure storage path exists."""
        if self._storage_path is None:
            data_dir = self.jarvis.settings.ensure_data_dir()
            self._storage_path = data_dir / "calendar.json"
        return self._storage_path

    def _load_events(self) -> None:
        """Load events from storage."""
        if self._loaded:
            return

        path = self._ensure_storage()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self._events = [CalendarEvent.from_dict(e) for e in data]
            except Exception:
                self._events = []
        self._loaded = True

    def _save_events(self) -> None:
        """Save events to storage."""
        path = self._ensure_storage()
        data = [e.to_dict() for e in self._events]
        path.write_text(json.dumps(data, indent=2))

    async def can_handle(self, text: str, context: "ConversationContext") -> bool:
        """Check if asking about calendar."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self._patterns)

    def _parse_datetime(self, text: str) -> datetime | None:
        """Parse a datetime from natural language."""
        now = datetime.now()
        text_lower = text.lower()

        # Relative dates
        if "today" in text_lower:
            return now.replace(hour=9, minute=0, second=0, microsecond=0)
        if "tomorrow" in text_lower:
            return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        # Day names
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(days):
            if day in text_lower:
                days_ahead = i - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (now + timedelta(days=days_ahead)).replace(
                    hour=9, minute=0, second=0, microsecond=0
                )

        # Time patterns
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            ampm = time_match.group(3)

            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0

            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        return None

    def _get_events_for_range(
        self, start: datetime, end: datetime
    ) -> list[CalendarEvent]:
        """Get events within a date range."""
        self._load_events()
        events = []

        for event in self._events:
            if start <= event.start <= end:
                events.append(event)
            elif event.recurring:
                # Check recurring events
                check_date = event.start
                while check_date <= end:
                    if start <= check_date <= end:
                        # Create instance of recurring event
                        instance = CalendarEvent(
                            id=f"{event.id}_{check_date.isoformat()}",
                            title=event.title,
                            start=check_date,
                            end=event.end,
                            location=event.location,
                            description=event.description,
                            all_day=event.all_day,
                        )
                        events.append(instance)
                        break

                    if event.recurring == "daily":
                        check_date += timedelta(days=1)
                    elif event.recurring == "weekly":
                        check_date += timedelta(weeks=1)
                    elif event.recurring == "monthly":
                        check_date = check_date.replace(
                            month=check_date.month + 1 if check_date.month < 12 else 1,
                            year=check_date.year if check_date.month < 12 else check_date.year + 1,
                        )
                    elif event.recurring == "yearly":
                        check_date = check_date.replace(year=check_date.year + 1)
                    else:
                        break

        return sorted(events, key=lambda e: e.start)

    async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
        """Handle calendar requests."""
        text_lower = text.lower()
        self._load_events()

        # Check for add/create intent
        if any(word in text_lower for word in ["add", "create", "schedule", "set up"]):
            return await self._add_event(text)

        # Check for delete/cancel intent
        if any(word in text_lower for word in ["cancel", "delete", "remove"]):
            return await self._delete_event(text)

        # Default: list events
        return await self._list_events(text)

    async def _list_events(self, text: str) -> SkillResult:
        """List upcoming events."""
        now = datetime.now()
        text_lower = text.lower()

        # Determine date range
        if "today" in text_lower:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            period = "today"
        elif "tomorrow" in text_lower:
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            period = "tomorrow"
        elif "this week" in text_lower or "week" in text_lower:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
            period = "this week"
        else:
            # Default to next 3 days
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=3)
            period = "the next few days"

        events = self._get_events_for_range(start, end)

        if not events:
            return SkillResult(
                success=True,
                response=f"You have nothing scheduled for {period}.",
            )

        response = f"Here's what's on your calendar for {period}: "
        for event in events:
            time_str = event.start.strftime("%I:%M %p") if not event.all_day else "All day"
            date_str = event.start.strftime("%A")
            response += f"{event.title} on {date_str} at {time_str}. "

        return SkillResult(
            success=True,
            response=response.strip(),
            data={"events": [e.to_dict() for e in events]},
        )

    async def _add_event(self, text: str) -> SkillResult:
        """Add a new event."""
        # Extract event title (text after "called" or between quotes)
        title_match = re.search(r'(?:called |titled |named )"?([^"]+)"?', text.lower())
        if not title_match:
            # Try to extract from the general structure
            title_match = re.search(
                r"(?:add|create|schedule|set up) (?:a |an )?(?:event|meeting|appointment)(?: (?:for|about|called))? (.+?)(?:\s+(?:on|at|for|tomorrow|today)|\s*$)",
                text.lower(),
            )

        if not title_match:
            return SkillResult(
                success=False,
                response="What would you like to call this event?",
            )

        title = title_match.group(1).strip()

        # Parse date/time
        event_time = self._parse_datetime(text)
        if not event_time:
            event_time = datetime.now() + timedelta(hours=1)
            event_time = event_time.replace(minute=0, second=0, microsecond=0)

        # Create event
        import uuid

        event = CalendarEvent(
            id=str(uuid.uuid4()),
            title=title.title(),
            start=event_time,
            end=event_time + timedelta(hours=1),
        )

        self._events.append(event)
        self._save_events()

        time_str = event_time.strftime("%A at %I:%M %p")
        return SkillResult(
            success=True,
            response=f"I've added '{event.title}' to your calendar for {time_str}.",
            data={"event": event.to_dict()},
        )

    async def _delete_event(self, text: str) -> SkillResult:
        """Delete an event."""
        # Try to find event by title
        text_lower = text.lower()

        for event in self._events:
            if event.title.lower() in text_lower:
                self._events.remove(event)
                self._save_events()
                return SkillResult(
                    success=True,
                    response=f"I've removed '{event.title}' from your calendar.",
                )

        return SkillResult(
            success=False,
            response="I couldn't find that event on your calendar.",
        )
