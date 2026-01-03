"""Extensible skills framework."""

from skills.argus_camera_skill import ArgusCameraSkill
from skills.base import Skill, SkillRegistry, SkillResult
from skills.calendar_skill import CalendarSkill
from skills.reminder_skill import ReminderSkill
from skills.time_skill import TimeSkill
from skills.weather_skill import WeatherSkill

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillResult",
    "ArgusCameraSkill",
    "CalendarSkill",
    "ReminderSkill",
    "TimeSkill",
    "WeatherSkill",
]
