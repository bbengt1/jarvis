"""Base skill interface and registry."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.context import ConversationContext
    from core.jarvis import Jarvis


@dataclass
class SkillResult:
    """Result from executing a skill."""

    success: bool
    response: str
    data: dict[str, Any] = field(default_factory=dict)
    speak: bool = True  # Whether to speak the response


class Skill(ABC):
    """Base class for J.A.R.V.I.S. skills.

    Skills are modular capabilities that can be registered and invoked.
    Each skill defines trigger patterns and an execute method.
    """

    name: str = "base_skill"
    description: str = "A base skill"
    triggers: list[str] = []  # Keywords/patterns that activate this skill

    def __init__(self, jarvis: "Jarvis") -> None:
        self.jarvis = jarvis

    @abstractmethod
    async def can_handle(self, text: str, context: "ConversationContext") -> bool:
        """Check if this skill can handle the given input.

        Args:
            text: User input text
            context: Current conversation context

        Returns:
            True if this skill should handle the input
        """
        ...

    @abstractmethod
    async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
        """Execute the skill.

        Args:
            text: User input text
            context: Current conversation context

        Returns:
            SkillResult with response and status
        """
        ...


class SkillRegistry:
    """Registry for managing and invoking skills."""

    def __init__(self) -> None:
        self._skills: list[Skill] = []

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills.append(skill)

    def unregister(self, skill_name: str) -> bool:
        """Unregister a skill by name."""
        for i, skill in enumerate(self._skills):
            if skill.name == skill_name:
                self._skills.pop(i)
                return True
        return False

    async def find_skill(
        self, text: str, context: "ConversationContext"
    ) -> Skill | None:
        """Find a skill that can handle the given input."""
        for skill in self._skills:
            if await skill.can_handle(text, context):
                return skill
        return None

    async def execute(
        self, text: str, context: "ConversationContext"
    ) -> SkillResult | None:
        """Find and execute a skill for the given input."""
        skill = await self.find_skill(text, context)
        if skill:
            return await skill.execute(text, context)
        return None

    def list_skills(self) -> list[tuple[str, str]]:
        """List all registered skills with descriptions."""
        return [(s.name, s.description) for s in self._skills]
