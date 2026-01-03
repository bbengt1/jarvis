"""Weather skill - provides weather information."""

import re
from typing import TYPE_CHECKING, Any

import httpx

from skills.base import Skill, SkillResult

if TYPE_CHECKING:
    from core.context import ConversationContext
    from core.jarvis import Jarvis


class WeatherSkill(Skill):
    """Provides current weather and forecasts.

    Uses Open-Meteo API (free, no API key required) with geocoding.
    """

    name = "weather"
    description = "Provides weather information and forecasts"
    triggers = ["weather", "temperature", "forecast", "rain", "sunny", "cold", "hot"]

    def __init__(self, jarvis: "Jarvis") -> None:
        super().__init__(jarvis)
        self._patterns = [
            r"(?:what(?:'s| is) the )?weather(?: like)?",
            r"(?:what(?:'s| is) the )?temperature",
            r"(?:is it |will it )?(rain|snow|sunny|cloudy)",
            r"(?:what(?:'s| is) the )?forecast",
            r"how(?:'s| is) the weather",
            r"(?:is it |how )?(cold|hot|warm) (?:outside|today)?",
        ]
        self._location_pattern = r"(?:in|at|for) ([a-zA-Z\s,]+?)(?:\?|$|\.)"
        self._client = httpx.AsyncClient(timeout=10.0)

        # Default location (can be configured via web UI)
        self._default_location = "New York"
        self._default_coords: tuple[float, float] | None = None

    async def can_handle(self, text: str, context: "ConversationContext") -> bool:
        """Check if asking about weather."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self._patterns)

    async def _geocode(self, location: str) -> tuple[float, float, str] | None:
        """Convert location name to coordinates."""
        try:
            response = await self._client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                name = result.get("name", location)
                country = result.get("country", "")
                full_name = f"{name}, {country}" if country else name
                return (result["latitude"], result["longitude"], full_name)
        except Exception:
            pass
        return None

    async def _get_weather(
        self, lat: float, lon: float
    ) -> dict[str, Any] | None:
        """Fetch weather data from Open-Meteo."""
        try:
            response = await self._client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                    "timezone": "auto",
                    "forecast_days": 3,
                },
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def _weather_code_to_description(self, code: int) -> str:
        """Convert WMO weather code to description."""
        codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail",
        }
        return codes.get(code, "unknown conditions")

    async def execute(self, text: str, context: "ConversationContext") -> SkillResult:
        """Get weather information."""
        # Extract location from text
        location = self._default_location
        if match := re.search(self._location_pattern, text.lower()):
            location = match.group(1).strip()

        # Geocode the location
        geo_result = await self._geocode(location)
        if not geo_result:
            return SkillResult(
                success=False,
                response=f"I couldn't find the location '{location}'. Please try a different city name.",
            )

        lat, lon, location_name = geo_result

        # Get weather data
        weather = await self._get_weather(lat, lon)
        if not weather:
            return SkillResult(
                success=False,
                response="I'm having trouble getting weather data right now. Please try again later.",
            )

        # Build response
        current = weather.get("current", {})
        daily = weather.get("daily", {})

        temp = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind = current.get("wind_speed_10m", "N/A")
        weather_code = current.get("weather_code", 0)
        conditions = self._weather_code_to_description(weather_code)

        response = f"In {location_name}, it's currently {temp}°F with {conditions}. "
        response += f"Humidity is {humidity}% and wind speed is {wind} mph."

        # Add forecast if asked
        text_lower = text.lower()
        if "forecast" in text_lower or "tomorrow" in text_lower or "week" in text_lower:
            if daily.get("time"):
                response += " Here's the forecast: "
                for i, date in enumerate(daily["time"][:3]):
                    high = daily["temperature_2m_max"][i]
                    low = daily["temperature_2m_min"][i]
                    rain_chance = daily["precipitation_probability_max"][i]
                    day_conditions = self._weather_code_to_description(daily["weather_code"][i])

                    day_name = "Today" if i == 0 else ("Tomorrow" if i == 1 else date)
                    response += f"{day_name}: {day_conditions}, high of {high}°F, low of {low}°F"
                    if rain_chance > 20:
                        response += f", {rain_chance}% chance of rain"
                    response += ". "

        return SkillResult(
            success=True,
            response=response.strip(),
            data={"weather": weather, "location": location_name},
        )

    async def close(self) -> None:
        """Cleanup."""
        await self._client.aclose()
