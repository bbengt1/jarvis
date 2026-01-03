"""Time and date skill - example skill implementation."""

import re
from datetime import datetime
from typing import TYPE_CHECKING

from skills.base import Skill, SkillResult

if TYPE_CHECKING:
    from core.context import ConversationContext
    from core.jarvis import Jarvis


class TimeSkill(Skill):
    """Provides time and date information."""

    name = "time"
    description = "Tells the current time and date"
    triggers = ["time", "date", "day", "what time", "what day", "what's the date"]

    def __init__(self, jarvis: "Jarvis") -> None:
        super().__init__(jarvis)
        self._patterns = [
            r"what(?:'s| is) the time",
            r"what time is it",
            r"tell me the time",
            r"what(?:'s| is) the date",
            r"what(?:'s| is) today(?:'s)? date",
            r"what day is it",
            r"what day of the week",
        ]

    async def can_handle(self, text: str, context: "ConversationContext") -> bool:
        """Check if asking about time or date."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self._patterns)

    async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
        """Return current time or date."""
        now = datetime.now()
        text_lower = text.lower()

        if "date" in text_lower or "day" in text_lower:
            if "day of the week" in text_lower or "what day is it" in text_lower:
                response = f"Today is {now.strftime('%A')}."
            else:
                response = f"Today is {now.strftime('%A, %B %d, %Y')}."
        else:
            response = f"The time is {now.strftime('%I:%M %p')}."

        return SkillResult(success=True, response=response)
