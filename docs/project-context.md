# Project Context: J.A.R.V.I.S.

> **Purpose:** Critical patterns and rules for AI agents implementing code
> **Optimized for:** LLM context efficiency
> **Last Updated:** 2026-01-03

## Quick Facts

| Attribute | Value |
|-----------|-------|
| Language | Python 3.11+ |
| Package Manager | uv (pyproject.toml) |
| Type Checking | mypy (strict mode) |
| Linting | ruff |
| Testing | pytest + pytest-asyncio |
| Architecture | Async-first, local-first |
| Database | SQLite + SQLAlchemy 2.x |
| Migrations | Alembic |
| Scheduler | APScheduler 4.x |
| Event Bus | MQTT (external) + asyncio (internal) |

## Critical Patterns

### 1. Async Everywhere

All I/O operations MUST be async. The codebase uses `asyncio` throughout.

```python
# CORRECT
async def process_data(self) -> str:
    result = await self.client.fetch()
    return result

# WRONG - blocks event loop
def process_data(self) -> str:
    result = self.client.fetch()  # Blocking!
    return result
```

### 2. Lazy Loading Pattern

Heavy resources (ML models, connections) are loaded lazily:

```python
def _load_model(self) -> Any:
    """Lazy load the model."""
    if self._model is None:
        self._model = SomeHeavyModel()
    return self._model
```

### 3. Settings with Pydantic

All configuration uses Pydantic v2:

```python
from pydantic_settings import BaseSettings

class MySettings(BaseSettings):
    value: str = "default"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",  # MYAPP__VALUE in env
    )
```

### 4. Provider Pattern for LLM

LLM providers inherit from `LLMProviderBase`:

```python
class MyProvider(LLMProviderBase):
    async def generate(self, messages, system=None, tools=None) -> str:
        ...

    async def generate_stream(self, messages, system=None):
        ...
        yield chunk
```

### 5. Skill Registration

Skills implement `can_handle()` and `execute()`:

```python
class MySkill(Skill):
    name = "my_skill"

    async def can_handle(self, text: str, context) -> bool:
        return "keyword" in text.lower()

    async def execute(self, text: str, context) -> SkillResult:
        return SkillResult(success=True, response="Done")
```

### 6. Database Models (SQLAlchemy 2.x)

All database models use SQLAlchemy 2.x with async support:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, func
from datetime import datetime

class UserPreference(Base):
    __tablename__ = "user_preferences"  # Plural snake_case

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
```

**Database Naming:**
- Tables: plural snake_case (`user_preferences`, `conversation_history`)
- Columns: snake_case (`created_at`, `user_id`)
- Primary Keys: `id` (integer)
- Foreign Keys: `{table}_id` (`user_id`, `conversation_id`)
- Indexes: `ix_{table}_{columns}`
- Timestamps: Always UTC

### 7. Event Bus Patterns

Internal events use asyncio pub/sub with typed events:

```python
from enum import StrEnum
from dataclasses import dataclass

class EventType(StrEnum):
    WAKE_WORD_DETECTED = "wake_word_detected"
    SPEECH_RECOGNIZED = "speech_recognized"
    HOME_EVENT = "home_event"
    MEMORY_UPDATED = "memory_updated"

@dataclass
class Event:
    type: EventType
    timestamp: datetime
    payload: dict[str, Any]
    source: str

# Subscribing
@event_bus.subscribe(EventType.HOME_EVENT)
async def handle_home_event(event: Event) -> None:
    ...

# Emitting
await event_bus.emit(Event(
    type=EventType.SPEECH_RECOGNIZED,
    timestamp=datetime.utcnow(),
    payload={"text": "Turn on lights", "confidence": 0.95},
    source="speech.recognition"
))
```

### 8. Memory Store Access

Always use MemoryStore interface, never raw SQL:

```python
memory = MemoryStore()

# Store preference
await memory.set_preference("default_temperature", "72")

# Record interaction
await memory.record_interaction(
    user_text="Turn on the lights",
    assistant_text="Done, Sir.",
    context={"skill": "home", "devices": ["light.living_room"]}
)

# Query with relevance
relevant = await memory.get_relevant_context(
    query="lights",
    limit=5,
    recency_weight=0.7
)
```

### 9. Graceful Degradation

Always implement fallback chains:

```python
async def get_llm_response(messages: list[Message]) -> str:
    try:
        return await llm.generate(messages)
    except CloudProviderError:
        logger.warning("Cloud LLM unavailable, falling back to Ollama")
        await llm.switch_provider(LLMProvider.OLLAMA)
        return await llm.generate(messages)
    except OllamaError:
        return "I apologize, Sir, but I'm having difficulty at the moment."
```

### 10. Concurrent Operations

Use `asyncio.gather` for independent operations:

```python
# CORRECT: Concurrent independent operations
results = await asyncio.gather(
    memory.get_preferences(),
    event_bus.get_recent_events(),
    scheduler.get_pending_jobs()
)

# WRONG: Sequential independent operations
prefs = await memory.get_preferences()  # Don't wait
events = await event_bus.get_recent_events()  # for these
jobs = await scheduler.get_pending_jobs()  # separately!
```

## File Conventions

| Location | Convention |
|----------|------------|
| `core/` | Orchestration, no external deps |
| `brain/` | LLM and NLP logic |
| `speech/` | Audio I/O |
| `vision/` | Camera and detection |
| `home/` | Smart home integration |
| `skills/` | One skill per file |
| `web/` | FastAPI routes |
| `memory/` | SQLAlchemy models, MemoryStore |
| `events/` | EventBus, EventType enum |
| `personality/` | System prompt, YAML config |
| `scheduler/` | APScheduler jobs |
| `users/` | User profiles, guest mode |
| `orchestration/` | Multi-step planner (Phase 3) |
| `server/` | Client/server protocol (Phase 3) |
| `tests/` | test_*.py files |

## Type Hints

Strict mypy - ALL functions need types:

```python
# Required
async def process(data: bytes) -> str | None:
    ...

# Use modern syntax
list[str]       # not List[str]
dict[str, Any]  # not Dict[str, Any]
str | None      # not Optional[str]
```

## Error Handling

Use specific exceptions, always cleanup:

```python
# Define module-specific exceptions
class MemoryError(Exception):
    """Base exception for memory operations."""
    pass

class MemoryNotFoundError(MemoryError):
    """Requested memory key not found."""
    pass

# Catch specific, log, handle gracefully
async def process_command(text: str) -> str:
    try:
        result = await skill.execute(text, context)
        return result.response
    except SkillNotFoundError:
        logger.warning(f"No skill matched: {text}")
        return await llm.generate_fallback(text)
    except ExternalServiceError as e:
        logger.error(f"External service failed: {e}")
        return "I'm having trouble connecting to that service, Sir."
```

## Import Order

Ruff enforces isort-style:

```python
# 1. Standard library
import asyncio
from collections.abc import AsyncIterator
from datetime import datetime

# 2. Third-party
import httpx
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local
from core.config import Settings
from brain.llm import LLMClient
from memory.store import MemoryStore
from events.bus import EventBus
```

## Testing

All tests are async-compatible:

```python
# pytest.ini_options: asyncio_mode = "auto"
import pytest
from memory.store import MemoryStore

async def test_memory_store() -> None:
    store = MemoryStore(test_session)
    await store.set_preference("key", "value")
    result = await store.get_preference("key")
    assert result == "value"

# Use fixtures for database
@pytest.fixture
async def memory_store(db_session: AsyncSession) -> MemoryStore:
    return MemoryStore(db_session)
```

## Don't Do

- Never block the event loop (use `run_in_executor` for CPU-bound)
- Never use `typing.List`, `typing.Dict` (use `list`, `dict`)
- Never hardcode secrets (use env vars or settings.json)
- Never print for logging in production code
- Never skip type hints
- Never use raw SQL (use MemoryStore interface)
- Never use raw dicts for data models (use Pydantic)
- Never ignore async (all I/O must be async)
- Never forget graceful degradation for external services
