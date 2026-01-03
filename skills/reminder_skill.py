"""Reminder skill - manages reminders with notifications."""

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from skills.base import Skill, SkillResult

if TYPE_CHECKING:
    from core.context import ConversationContext
    from core.jarvis import Jarvis


@dataclass
class Reminder:
    """A reminder."""

    id: str
    message: str
    trigger_time: datetime
    created_at: datetime
    completed: bool = False
    recurring: str = ""  # daily, weekly, or empty
    notified: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["trigger_time"] = self.trigger_time.isoformat()
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Reminder":
        """Create from dictionary."""
        data["trigger_time"] = datetime.fromisoformat(data["trigger_time"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class ReminderSkill(Skill):
    """Manages reminders with time-based triggers.

    Supports natural language time parsing and recurring reminders.
    """

    name = "reminders"
    description = "Sets and manages reminders"
    triggers = ["remind", "reminder", "remember", "don't forget", "alert me"]

    def __init__(self, jarvis: "Jarvis") -> None:
        super().__init__(jarvis)
        self._patterns = [
            r"remind me (?:to |about )?",
            r"set (?:a )?reminder",
            r"(?:don't forget|remember) to",
            r"(?:what are |show |list )(?:my )?reminders",
            r"(?:cancel|delete|remove|clear) (?:the |my )?reminder",
            r"alert me (?:to |about |when )?",
        ]
        self._reminders: list[Reminder] = []
        self._storage_path: Path | None = None
        self._loaded = False
        self._check_task: asyncio.Task[Any] | None = None
        self._running = False

    def _ensure_storage(self) -> Path:
        """Ensure storage path exists."""
        if self._storage_path is None:
            data_dir = self.jarvis.settings.ensure_data_dir()
            self._storage_path = data_dir / "reminders.json"
        return self._storage_path

    def _load_reminders(self) -> None:
        """Load reminders from storage."""
        if self._loaded:
            return

        path = self._ensure_storage()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self._reminders = [Reminder.from_dict(r) for r in data]
                # Filter out completed non-recurring reminders
                self._reminders = [
                    r for r in self._reminders
                    if not r.completed or r.recurring
                ]
            except Exception:
                self._reminders = []
        self._loaded = True

    def _save_reminders(self) -> None:
        """Save reminders to storage."""
        path = self._ensure_storage()
        data = [r.to_dict() for r in self._reminders]
        path.write_text(json.dumps(data, indent=2))

    async def can_handle(self, text: str, context: "ConversationContext") -> bool:
        """Check if asking about reminders."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self._patterns)

    def _parse_time(self, text: str) -> datetime | None:
        """Parse time from natural language."""
        now = datetime.now()
        text_lower = text.lower()

        # Duration patterns
        duration_patterns = [
            (r"in (\d+) minutes?", lambda m: now + timedelta(minutes=int(m))),
            (r"in (\d+) hours?", lambda m: now + timedelta(hours=int(m))),
            (r"in (\d+) days?", lambda m: now + timedelta(days=int(m))),
            (r"in half an hour", lambda m: now + timedelta(minutes=30)),
            (r"in an hour", lambda m: now + timedelta(hours=1)),
        ]

        for pattern, time_fn in duration_patterns:
            if match := re.search(pattern, text_lower):
                return time_fn(int(match.group(1)) if match.lastindex else 0)

        # Specific times
        if "tomorrow" in text_lower:
            base = now + timedelta(days=1)
        elif "today" in text_lower:
            base = now
        else:
            base = now

        # Parse time of day
        time_match = re.search(r"at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            ampm = time_match.group(3)

            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0

            return base.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Time of day words
        if "morning" in text_lower:
            return base.replace(hour=9, minute=0, second=0, microsecond=0)
        if "afternoon" in text_lower:
            return base.replace(hour=14, minute=0, second=0, microsecond=0)
        if "evening" in text_lower:
            return base.replace(hour=18, minute=0, second=0, microsecond=0)
        if "night" in text_lower:
            return base.replace(hour=21, minute=0, second=0, microsecond=0)

        # Default to 1 hour from now if no time specified
        return now + timedelta(hours=1)

    def _extract_message(self, text: str) -> str:
        """Extract the reminder message from text."""
        # Remove trigger phrases
        message = text.lower()
        remove_patterns = [
            r"remind me (?:to |about )?",
            r"set (?:a )?reminder (?:to |for |about )?",
            r"(?:don't forget|remember) to ",
            r"alert me (?:to |about )?",
            r"in \d+ (?:minutes?|hours?|days?)",
            r"at \d{1,2}(?::\d{2})?\s*(?:am|pm)?",
            r"tomorrow",
            r"today",
            r"(?:this )?(?:morning|afternoon|evening|night)",
            r"every (?:day|week|month)",
        ]

        for pattern in remove_patterns:
            message = re.sub(pattern, "", message)

        # Clean up
        message = re.sub(r"\s+", " ", message).strip()
        return message.capitalize() if message else "Reminder"

    async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
        """Handle reminder requests."""
        text_lower = text.lower()
        self._load_reminders()

        # Check for list intent
        if any(word in text_lower for word in ["what are", "show", "list"]):
            return await self._list_reminders()

        # Check for delete intent
        if any(word in text_lower for word in ["cancel", "delete", "remove", "clear"]):
            return await self._delete_reminder(text)

        # Default: create reminder
        return await self._create_reminder(text)

    async def _create_reminder(self, text: str) -> SkillResult:
        """Create a new reminder."""
        trigger_time = self._parse_time(text)
        if not trigger_time:
            trigger_time = datetime.now() + timedelta(hours=1)

        message = self._extract_message(text)

        # Check for recurring
        text_lower = text.lower()
        recurring = ""
        if "every day" in text_lower or "daily" in text_lower:
            recurring = "daily"
        elif "every week" in text_lower or "weekly" in text_lower:
            recurring = "weekly"

        reminder = Reminder(
            id=str(uuid.uuid4()),
            message=message,
            trigger_time=trigger_time,
            created_at=datetime.now(),
            recurring=recurring,
        )

        self._reminders.append(reminder)
        self._save_reminders()

        # Format response
        if trigger_time.date() == datetime.now().date():
            time_str = f"today at {trigger_time.strftime('%I:%M %p')}"
        elif trigger_time.date() == (datetime.now() + timedelta(days=1)).date():
            time_str = f"tomorrow at {trigger_time.strftime('%I:%M %p')}"
        else:
            time_str = trigger_time.strftime("%A, %B %d at %I:%M %p")

        recurring_str = f" ({recurring})" if recurring else ""

        return SkillResult(
            success=True,
            response=f"I'll remind you to '{message}' {time_str}{recurring_str}.",
            data={"reminder": reminder.to_dict()},
        )

    async def _list_reminders(self) -> SkillResult:
        """List active reminders."""
        active = [r for r in self._reminders if not r.completed]

        if not active:
            return SkillResult(
                success=True,
                response="You don't have any active reminders.",
            )

        # Sort by trigger time
        active.sort(key=lambda r: r.trigger_time)

        response = f"You have {len(active)} reminder{'s' if len(active) != 1 else ''}: "
        for reminder in active[:5]:  # Limit to 5
            time_str = reminder.trigger_time.strftime("%I:%M %p on %A")
            recurring_str = f" ({reminder.recurring})" if reminder.recurring else ""
            response += f"'{reminder.message}' at {time_str}{recurring_str}. "

        if len(active) > 5:
            response += f"And {len(active) - 5} more."

        return SkillResult(
            success=True,
            response=response.strip(),
            data={"reminders": [r.to_dict() for r in active]},
        )

    async def _delete_reminder(self, text: str) -> SkillResult:
        """Delete a reminder."""
        text_lower = text.lower()

        # Try to match by message content
        for reminder in self._reminders:
            if reminder.message.lower() in text_lower or text_lower in reminder.message.lower():
                self._reminders.remove(reminder)
                self._save_reminders()
                return SkillResult(
                    success=True,
                    response=f"I've cancelled the reminder '{reminder.message}'.",
                )

        # Check for "all" or "clear all"
        if "all" in text_lower:
            count = len(self._reminders)
            self._reminders.clear()
            self._save_reminders()
            return SkillResult(
                success=True,
                response=f"I've cleared all {count} reminders.",
            )

        return SkillResult(
            success=False,
            response="I couldn't find that reminder. Try saying 'list my reminders' to see them.",
        )

    async def check_and_trigger(self) -> list[Reminder]:
        """Check for due reminders and return those that should trigger."""
        self._load_reminders()
        now = datetime.now()
        triggered = []

        for reminder in self._reminders:
            if reminder.completed or reminder.notified:
                continue

            if reminder.trigger_time <= now:
                triggered.append(reminder)
                reminder.notified = True

                if reminder.recurring:
                    # Schedule next occurrence
                    if reminder.recurring == "daily":
                        reminder.trigger_time += timedelta(days=1)
                    elif reminder.recurring == "weekly":
                        reminder.trigger_time += timedelta(weeks=1)
                    reminder.notified = False
                else:
                    reminder.completed = True

        if triggered:
            self._save_reminders()

        return triggered

    async def start_background_check(self, callback: Any) -> None:
        """Start background task to check reminders periodically."""
        self._running = True

        async def check_loop() -> None:
            while self._running:
                triggered = await self.check_and_trigger()
                for reminder in triggered:
                    await callback(reminder)
                await asyncio.sleep(30)  # Check every 30 seconds

        self._check_task = asyncio.create_task(check_loop())

    async def close(self) -> None:
        """Stop background task."""
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
