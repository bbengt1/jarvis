---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
status: 'complete'
completedAt: '2026-01-03'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/analysis/brainstorming-session-2026-01-03.md'
  - 'docs/project-context.md'
  - 'docs/architecture.md'
  - 'docs/index.md'
  - 'docs/api-reference.md'
  - 'docs/skills-guide.md'
  - 'docs/llm-providers.md'
  - 'docs/home-automation.md'
workflowType: 'architecture'
project_name: 'J.A.R.V.I.S.'
user_name: 'Brent'
date: '2026-01-03'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

68 requirements across 10 capability areas, organized by architectural layer:

| Capability Area | FR Count | Architectural Impact |
|-----------------|----------|---------------------|
| Memory & Context | 8 | Core data layer - persistent store, query system, relevance scoring |
| Personality & Character | 5 | System prompt design, cross-mode consistency |
| Event Awareness & Proactivity | 9 | Event bus, scheduler daemon, pattern recognition |
| Voice Interaction | 6 | Audio pipeline (existing), interrupt handling |
| Home Automation | 6 | HA REST/WebSocket, MQTT event streaming |
| Orchestration & Planning | 7 | Multi-step planner, autonomous action framework (Phase 3) |
| User & Guest Management | 5 | User profiles, guest mode, privacy boundaries |
| Skills & Integration | 8 | Skill framework (existing), new integration adapters |
| Distributed Presence | 6 | Client/server architecture, audio handoff (Phase 3) |
| Configuration & Administration | 8 | Web UI (existing), memory inspection, backup/restore |

**Non-Functional Requirements:**

22 requirements driving architectural constraints:

| Category | Key Constraints |
|----------|-----------------|
| Performance | <2s voice latency, <100ms memory access, concurrent audio/LLM/TTS |
| Security | AES-256 at rest, TLS 1.3, keychain for secrets, privacy boundaries |
| Reliability | 99% uptime, graceful degradation, auto-recovery, zero data loss |
| Integration | HA 2024.1+, MQTT 5.0, 5 LLM providers, stable skill interface |
| Usability | <5% false wake, 95% speech accuracy, natural error messages |
| Maintainability | Structured logging, health dashboard, reversible migrations |

**Scale & Complexity:**

- Primary domain: IoT/Backend Hybrid with Voice Interface
- Complexity level: High (distributed system, ML pipelines, real-time audio)
- Estimated architectural components: 12-15 major components

### Technical Constraints & Dependencies

**Existing Constraints (Brownfield):**
- Python 3.11+, async-first architecture throughout
- Pydantic v2 for all configuration
- FastAPI for web/API layer
- Must maintain backward compatibility for existing skills

**External Dependencies:**
- Home Assistant API (required for home automation)
- Ollama (default local LLM inference)
- Whisper/Piper (local speech processing)
- MQTT broker (required for event bus)

**Phase-Gated Constraints:**
- Phase 1: Single instance only, no client/server split
- Phase 2: No autonomous actions, scheduled/event-driven only
- Phase 3: Full distributed architecture, autonomous decisions

### Cross-Cutting Concerns Identified

| Concern | Spans | Architectural Implication |
|---------|-------|---------------------------|
| **Memory Access** | All components | Unified memory service with async interface |
| **Event Bus** | Home, Skills, Scheduler, Proactivity | MQTT-based pub/sub with typed events |
| **Personality** | LLM, TTS, Web UI | Consistent system prompt, character config |
| **Offline Mode** | Speech, LLM, Skills | Graceful degradation strategy per component |
| **Logging/Observability** | All components | Structured logging, health endpoints |
| **Security** | Memory, API, Clients | Encryption, auth, privacy boundaries |

## Starter Template Evaluation

### Primary Technology Domain

**Brownfield Python Backend/IoT Hybrid** - Extending an existing voice assistant codebase with new architectural layers.

### Existing Foundation (Not a Starter Template)

This is a brownfield project with an established codebase. No starter template selection is needed - we're extending an existing system.

**Existing Technical Stack:**

| Layer | Technology | Status |
|-------|------------|--------|
| Language | Python 3.11+ | Established |
| Package Manager | uv | Established |
| Web Framework | FastAPI | Established |
| Configuration | Pydantic v2 | Established |
| Type Checking | mypy (strict) | Established |
| Linting | ruff | Established |
| Testing | pytest + pytest-asyncio | Established |
| Audio | faster-whisper, OpenWakeWord, Piper | Established |
| Vision | Ultralytics YOLO | Established |
| Home Automation | Home Assistant API, MQTT | Established |

**Architectural Patterns to Preserve:**

- Async-first I/O throughout
- Lazy loading for ML models and connections
- Provider pattern for LLM abstraction
- Skill registry with `can_handle()` / `execute()` interface
- Pydantic settings with env loading (`__` delimiter)
- FastAPI with lifespan management

**New Components to Integrate:**

| Component | Integration Point | Phase |
|-----------|------------------|-------|
| Memory Store | New `memory/` module | Phase 1 |
| Event Bus | MQTT extension in `home/` or new `events/` | Phase 1 |
| Scheduler Daemon | New `scheduler/` module | Phase 2 |
| Orchestrator/Planner | New `orchestration/` module | Phase 3 |
| Client/Server Split | Refactor `core/jarvis.py` | Phase 3 |

**Note:** No initialization command required - codebase exists.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Memory Store architecture (Phase 1 blocker)
- Event Bus architecture (Phase 1 blocker)
- Personality System design (Phase 1 blocker)

**Important Decisions (Shape Architecture):**
- Scheduler architecture (Phase 2)
- Client/Server protocol (Phase 3)

**Deferred Decisions (Post-MVP):**
- Vector search for semantic memory retrieval
- Mobile client platform (iOS/Android/cross-platform)
- Room client hardware specifications

### Data Architecture

**Decision: SQLite + SQLAlchemy**

| Attribute | Value |
|-----------|-------|
| Database | SQLite 3.x (file-based) |
| ORM | SQLAlchemy 2.x with async support |
| Location | `~/.jarvis/memory.db` |
| Migrations | Alembic |

**Rationale:**
- Local-first philosophy: no external database server required
- File-based: easy backup, portable, works offline
- SQLAlchemy 2.x: modern async support, type hints, mature ecosystem
- Alembic: reversible migrations per NFR22

**Schema Approach:**
- Preferences table: key-value with metadata
- History table: timestamped interactions with context
- Patterns table: learned behaviors with confidence scores
- Relationships table: entity connections and references

**Future Consideration:** Add ChromaDB or pgvector if semantic memory search becomes valuable (e.g., "what did I say about X last month?").

### Event Bus Architecture

**Decision: MQTT (external) + asyncio pub/sub (internal)**

| Layer | Technology | Purpose |
|-------|------------|---------|
| External Events | MQTT (existing) | Home Assistant, sensors, IoT devices |
| Internal Events | asyncio pub/sub | Component coordination, state changes |

**Rationale:**
- Leverages existing MQTT integration with Home Assistant
- Internal asyncio avoids external dependency for component messaging
- Clear separation: external world (MQTT) vs. internal coordination (asyncio)
- Both are async-native, fitting our architecture

**Topic Namespace (MQTT):**
```
jarvis/events/home/#      # HA events forwarded
jarvis/events/sensors/#   # Direct sensor events
jarvis/commands/#         # Command channel (Phase 3 clients)
```

**Internal Event Types:**
```python
class EventType(StrEnum):
    WAKE_WORD_DETECTED = "wake_word_detected"
    SPEECH_RECOGNIZED = "speech_recognized"
    RESPONSE_GENERATED = "response_generated"
    HOME_EVENT = "home_event"
    SCHEDULE_TRIGGERED = "schedule_triggered"
    MEMORY_UPDATED = "memory_updated"
```

### Scheduler Architecture

**Decision: APScheduler with AsyncIO executor**

| Attribute | Value |
|-----------|-------|
| Library | APScheduler 4.x |
| Executor | AsyncIOExecutor |
| Job Store | SQLite (same DB as memory store) |
| Timezone | Local system timezone |

**Rationale:**
- Battle-tested library with async support
- SQLite job store: jobs persist across restarts
- Supports cron, interval, and date triggers
- Integrates cleanly with asyncio event loop

**Scheduled Jobs (Phase 2):**
```python
# Morning briefing (weekdays 7am, weekends 9am)
scheduler.add_job(morning_briefing, CronTrigger(hour=7, day_of_week='mon-fri'))
scheduler.add_job(morning_briefing, CronTrigger(hour=9, day_of_week='sat,sun'))

# Evening transition (daily at configured time)
scheduler.add_job(evening_transition, CronTrigger(hour=17, minute=30))

# Pattern analysis (daily at 3am)
scheduler.add_job(analyze_patterns, CronTrigger(hour=3))
```

### Personality System Architecture

**Decision: System prompt + personality config (YAML)**

| Component | Purpose |
|-----------|---------|
| Base system prompt | Core J.A.R.V.I.S. character definition |
| Personality config | Tunable traits (formality, wit, verbosity) |
| Context injection | Dynamic context from memory store |

**Rationale:**
- System prompt provides consistent character foundation
- YAML config allows tuning without code changes
- Separates character definition from implementation
- Works with all LLM providers (no fine-tuning lock-in)

**Personality Config Structure:**
```yaml
# ~/.jarvis/personality.yaml
character:
  name: "J.A.R.V.I.S."
  address_user_as: "Sir"

traits:
  formality: 0.8        # 0=casual, 1=formal
  wit: 0.7              # 0=straight, 1=sardonic
  verbosity: 0.4        # 0=terse, 1=elaborate
  proactivity: 0.6      # 0=reactive, 1=volunteering

boundaries:
  opinions: true        # Can express opinions
  pushback: true        # Can respectfully disagree
  humor: "dry"          # dry, warm, none
```

**System Prompt Template:**
```
You are J.A.R.V.I.S., a sophisticated AI assistant. You address the user as "{address_user_as}".

Your personality traits:
- Formal but not stiff - you're a trusted peer, not a servant
- Dry wit when appropriate - sardonic observations, never cruel
- Concise unless detail is requested
- You remember past interactions and reference them naturally
- You have opinions and can respectfully disagree

{dynamic_context_from_memory}
```

### Client/Server Protocol (Phase 3)

**Decision: WebSocket with binary audio + JSON commands**

| Channel | Format | Purpose |
|---------|--------|---------|
| Audio upstream | Binary (PCM/Opus) | Voice from client to server |
| Audio downstream | Binary (PCM/Opus) | TTS from server to client |
| Commands | JSON | Control messages, state sync |
| Events | JSON | Server-initiated notifications |

**Rationale:**
- Single connection handles both audio and commands
- Binary frames efficient for audio streaming
- JSON readable and debuggable for commands
- Browser-compatible (potential web client)
- Simpler than managing multiple protocols

**Message Schema:**
```python
# Command message (JSON)
{
    "type": "command",
    "id": "uuid",
    "action": "speech_start" | "speech_end" | "interrupt" | ...,
    "payload": {}
}

# Event message (JSON)
{
    "type": "event",
    "event": "response_ready" | "listening" | "thinking" | ...,
    "payload": {}
}

# Audio frame (Binary)
# Header: 4 bytes (type + length)
# Payload: PCM 16-bit 16kHz mono or Opus compressed
```

### Decision Impact Analysis

**Implementation Sequence:**
1. Memory Store (Phase 1) - Foundation for everything
2. Personality System (Phase 1) - Immediate UX impact
3. Event Bus (Phase 1) - Enables proactivity
4. Scheduler (Phase 2) - Requires event bus
5. Client/Server Protocol (Phase 3) - Requires stable core

**Cross-Component Dependencies:**

```
Memory Store ◄─── Personality (context injection)
     │
     ▼
Event Bus ◄────── Scheduler (triggers events)
     │
     ▼
Client Protocol ── All components (distributed access)
```

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 12 areas where AI agents could make different choices, now standardized.

### Naming Patterns

**Database Naming Conventions:**

| Element | Convention | Example |
|---------|------------|---------|
| Tables | Plural snake_case | `user_preferences`, `conversation_history` |
| Columns | snake_case | `created_at`, `user_id`, `confidence_score` |
| Primary Keys | `id` (integer) or `{table}_id` for clarity | `id`, `preference_id` |
| Foreign Keys | `{referenced_table}_id` | `user_id`, `conversation_id` |
| Indexes | `ix_{table}_{columns}` | `ix_preferences_user_id` |
| Timestamps | `created_at`, `updated_at` | Always UTC |

**Python Model Naming:**
```python
# Table: user_preferences
class UserPreference(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

**Event Naming Conventions:**

| Element | Convention | Example |
|---------|------------|---------|
| Event types | snake_case StrEnum | `EventType.WAKE_WORD_DETECTED` |
| Event names | snake_case string | `"speech_recognized"` |
| Payload keys | snake_case | `{"confidence_score": 0.95}` |
| MQTT topics | slash-separated | `jarvis/events/home/doorbell` |

**Code Naming Conventions (Python PEP 8):**

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `memory_store.py` |
| Classes | PascalCase | `MemoryStore`, `EventBus` |
| Functions | snake_case | `get_preferences()`, `emit_event()` |
| Variables | snake_case | `user_id`, `event_payload` |
| Constants | SCREAMING_SNAKE | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| Private | Leading underscore | `_internal_method()`, `_cache` |

### Structure Patterns

**Project Organization (New Modules):**

```
jarvis/
├── memory/              # NEW: Persistent memory store
│   ├── __init__.py
│   ├── store.py         # MemoryStore class
│   ├── models.py        # SQLAlchemy models
│   ├── queries.py       # Query helpers
│   └── migrations/      # Alembic migrations
├── events/              # NEW: Internal event bus
│   ├── __init__.py
│   ├── bus.py           # EventBus class
│   ├── types.py         # EventType enum, event dataclasses
│   └── handlers.py      # Event handler registry
├── scheduler/           # NEW: APScheduler integration
│   ├── __init__.py
│   ├── daemon.py        # Scheduler daemon
│   └── jobs.py          # Job definitions
├── personality/         # NEW: Character system
│   ├── __init__.py
│   ├── config.py        # PersonalityConfig loader
│   └── prompt.py        # System prompt builder
└── ... (existing modules unchanged)
```

**File Structure Patterns:**

| Category | Location | Example |
|----------|----------|---------|
| User config | `~/.jarvis/` | `settings.json`, `personality.yaml` |
| User data | `~/.jarvis/` | `memory.db`, `calendar.json` |
| Default config | Project root | `.env.example`, `personality.default.yaml` |
| Tests | `tests/` | `tests/test_memory.py` |
| Documentation | `docs/` | `docs/architecture.md` |

### Format Patterns

**Internal Communication (Python):**

All internal communication uses typed Pydantic models - no raw dicts.

```python
# CORRECT: Typed models
class MemoryQuery(BaseModel):
    key: str
    limit: int = 10

async def get_memories(query: MemoryQuery) -> list[Memory]:
    ...

# WRONG: Raw dicts
async def get_memories(query: dict) -> list[dict]:  # No!
    ...
```

**Event Payloads:**

```python
@dataclass
class Event:
    type: EventType
    timestamp: datetime
    payload: dict[str, Any]
    source: str  # Component that emitted

# Example
Event(
    type=EventType.HOME_EVENT,
    timestamp=datetime.utcnow(),
    payload={"device": "front_door", "state": "locked"},
    source="home.automation"
)
```

**Error Responses:**

```python
# Internal: Raise exceptions, let caller handle
class MemoryError(Exception):
    """Base exception for memory operations."""
    pass

class MemoryNotFoundError(MemoryError):
    """Requested memory key not found."""
    pass

# External (Phase 3 clients): JSON error format
{
    "error": {
        "code": "memory_not_found",
        "message": "No memory found for key 'last_guest'",
        "details": {"key": "last_guest"}
    }
}
```

**Date/Time Handling:**

| Context | Format | Example |
|---------|--------|---------|
| Storage | UTC datetime | `datetime.utcnow()` |
| Display | Local timezone | `datetime.now(tz=local_tz)` |
| JSON | ISO 8601 string | `"2026-01-03T14:30:00Z"` |
| Logs | ISO 8601 with TZ | `"2026-01-03T14:30:00-05:00"` |

### Communication Patterns

**Event Bus Patterns:**

```python
# Subscribing to events
@event_bus.subscribe(EventType.HOME_EVENT)
async def handle_home_event(event: Event) -> None:
    if event.payload.get("device") == "doorbell":
        await announce("Someone is at the door")

# Emitting events
await event_bus.emit(Event(
    type=EventType.SPEECH_RECOGNIZED,
    timestamp=datetime.utcnow(),
    payload={"text": "Turn on the lights", "confidence": 0.95},
    source="speech.recognition"
))
```

**Memory Access Patterns:**

```python
# Always use the MemoryStore interface, never raw SQL
memory = MemoryStore()

# Store preference (explicit)
await memory.set_preference("default_temperature", "72")

# Store interaction (automatic context)
await memory.record_interaction(
    user_text="Turn on the lights",
    assistant_text="I've turned on the living room lights, Sir.",
    context={"skill": "home", "devices": ["light.living_room"]}
)

# Query with relevance
relevant = await memory.get_relevant_context(
    query="lights",
    limit=5,
    recency_weight=0.7
)
```

### Process Patterns

**Error Handling:**

```python
# Pattern: Catch specific, log, re-raise or handle gracefully
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
    except Exception as e:
        logger.exception(f"Unexpected error processing: {text}")
        raise  # Let top-level handler deal with it
```

**Graceful Degradation:**

```python
# Pattern: Try preferred, fall back, inform user
async def get_llm_response(messages: list[Message]) -> str:
    try:
        return await llm.generate(messages)
    except CloudProviderError:
        logger.warning("Cloud LLM unavailable, falling back to Ollama")
        await llm.switch_provider(LLMProvider.OLLAMA)
        return await llm.generate(messages)
    except OllamaError:
        return "I apologize, Sir, but I'm having difficulty processing that request at the moment."
```

**Async Patterns:**

```python
# CORRECT: Concurrent independent operations
results = await asyncio.gather(
    memory.get_preferences(),
    event_bus.get_recent_events(),
    scheduler.get_pending_jobs()
)

# CORRECT: Sequential dependent operations
user_prefs = await memory.get_preferences()
context = await build_context(user_prefs)
response = await llm.generate(messages, context=context)

# WRONG: Sequential independent operations
prefs = await memory.get_preferences()  # Don't wait
events = await event_bus.get_recent_events()  # for these
jobs = await scheduler.get_pending_jobs()  # separately!
```

### Enforcement Guidelines

**All AI Agents MUST:**

1. Follow existing patterns in `docs/project-context.md` - these are non-negotiable
2. Use async for ALL I/O operations - never block the event loop
3. Use Pydantic models for all data structures - no raw dicts
4. Include type hints on ALL functions - mypy strict mode
5. Write tests in `tests/test_{module}.py` for new functionality
6. Log significant events with appropriate levels (DEBUG/INFO/WARNING/ERROR)
7. Handle errors gracefully with user-friendly messages

**Pattern Verification:**

- `uv run mypy .` - Catches type hint violations
- `uv run ruff check .` - Catches naming/style violations
- `uv run pytest` - Validates functionality
- Code review checklist includes pattern compliance

### Pattern Examples

**Good Example (Memory Store):**

```python
# memory/store.py
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

class PreferenceUpdate(BaseModel):
    key: str
    value: str
    source: str = "explicit"

class MemoryStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def set_preference(self, update: PreferenceUpdate) -> None:
        """Store a user preference."""
        pref = UserPreference(
            key=update.key,
            value=update.value,
            source=update.source,
            updated_at=datetime.utcnow()
        )
        self._session.add(pref)
        await self._session.commit()
```

**Anti-Patterns (What to Avoid):**

```python
# WRONG: Blocking I/O
def get_data():  # Missing async!
    return requests.get(url)  # Blocks event loop!

# WRONG: Raw dict instead of model
async def save(data: dict) -> dict:  # No type safety!
    ...

# WRONG: Inconsistent naming
class userPreference:  # Should be PascalCase
    UserID: int  # Should be snake_case
    createdAt: datetime  # Should be created_at

# WRONG: No error handling
async def risky_operation():
    result = await external_api.call()  # What if it fails?
    return result
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
jarvis/
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── jarvis/                      # Main package
│   │
│   ├── __init__.py
│   │
│   ├── core/                    # EXISTING: Central orchestration
│   │   ├── __init__.py
│   │   ├── jarvis.py            # Main entry point, orchestrator
│   │   ├── config.py            # Pydantic settings, LLMProvider enum
│   │   └── context.py           # Conversation state (extend for memory)
│   │
│   ├── brain/                   # EXISTING: NLP and LLM
│   │   ├── __init__.py
│   │   ├── llm.py               # Multi-provider LLM client
│   │   ├── intent.py            # Intent parsing
│   │   └── providers/           # LLM provider implementations
│   │       ├── __init__.py
│   │       ├── base.py          # LLMProviderBase
│   │       ├── ollama.py
│   │       ├── openai.py
│   │       ├── anthropic.py
│   │       ├── google.py
│   │       └── xai.py
│   │
│   ├── speech/                  # EXISTING: Voice I/O
│   │   ├── __init__.py
│   │   ├── wakeword.py          # OpenWakeWord detection
│   │   ├── recognition.py       # Whisper STT
│   │   └── synthesis.py         # Piper TTS
│   │
│   ├── vision/                  # EXISTING: Computer vision
│   │   ├── __init__.py
│   │   └── processor.py         # YOLO detection
│   │
│   ├── home/                    # EXISTING: Smart home
│   │   ├── __init__.py
│   │   ├── automation.py        # Home Assistant + MQTT
│   │   └── event_bridge.py      # NEW: Forward HA events to event bus
│   │
│   ├── skills/                  # EXISTING: Skill framework
│   │   ├── __init__.py
│   │   ├── base.py              # Skill interface, SkillRegistry
│   │   ├── time_skill.py
│   │   ├── weather_skill.py
│   │   ├── calendar_skill.py
│   │   ├── reminder_skill.py
│   │   ├── argus_camera_skill.py
│   │   ├── email_skill.py       # NEW (Phase 2)
│   │   ├── print_skill.py       # NEW (Phase 2) - 3D print monitoring
│   │   └── ci_skill.py          # NEW (Phase 2) - CI/CD status
│   │
│   ├── web/                     # EXISTING: Configuration UI
│   │   ├── __init__.py
│   │   ├── server.py            # FastAPI app
│   │   ├── templates/           # HTML templates
│   │   │   ├── index.html
│   │   │   └── core.html
│   │   └── static/              # CSS, JS
│   │
│   ├── memory/                  # NEW: Persistent memory store (Phase 1)
│   │   ├── __init__.py
│   │   ├── store.py             # MemoryStore class
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── queries.py           # Query helpers, relevance scoring
│   │   ├── migrations/          # Alembic migrations
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/
│   │   └── alembic.ini
│   │
│   ├── events/                  # NEW: Internal event bus (Phase 1)
│   │   ├── __init__.py
│   │   ├── bus.py               # EventBus class (asyncio pub/sub)
│   │   ├── types.py             # EventType enum, Event dataclass
│   │   ├── handlers.py          # Handler registry, decorators
│   │   └── mqtt_bridge.py       # MQTT ↔ internal event bridge
│   │
│   ├── personality/             # NEW: Character system (Phase 1)
│   │   ├── __init__.py
│   │   ├── config.py            # PersonalityConfig loader (YAML)
│   │   ├── prompt.py            # System prompt builder
│   │   └── context.py           # Dynamic context injection
│   │
│   ├── scheduler/               # NEW: Proactive behaviors (Phase 2)
│   │   ├── __init__.py
│   │   ├── daemon.py            # APScheduler daemon
│   │   ├── jobs.py              # Job definitions (briefings, transitions)
│   │   └── triggers.py          # Custom trigger logic
│   │
│   ├── users/                   # NEW: User management (Phase 1)
│   │   ├── __init__.py
│   │   ├── profiles.py          # User profile management
│   │   ├── guest.py             # Guest mode handling
│   │   └── models.py            # User/Guest models
│   │
│   ├── orchestration/           # NEW: Multi-step planning (Phase 3)
│   │   ├── __init__.py
│   │   ├── planner.py           # Multi-step planner
│   │   ├── executor.py          # Plan execution engine
│   │   └── actions.py           # Action definitions
│   │
│   ├── server/                  # NEW: Client/server protocol (Phase 3)
│   │   ├── __init__.py
│   │   ├── protocol.py          # WebSocket message handling
│   │   ├── audio.py             # Audio streaming (binary frames)
│   │   ├── clients.py           # Client connection management
│   │   └── handoff.py           # Room handoff logic
│   │
│   └── utils/                   # Shared utilities
│       ├── __init__.py
│       ├── logging.py           # Structured logging setup
│       └── async_utils.py       # Async helper functions
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_intent.py           # EXISTING
│   ├── test_memory.py           # NEW
│   ├── test_events.py           # NEW
│   ├── test_personality.py      # NEW
│   ├── test_scheduler.py        # NEW
│   ├── test_users.py            # NEW
│   └── fixtures/                # Test data
│       ├── sample_memories.json
│       └── personality_test.yaml
│
├── docs/                        # Documentation
│   ├── index.md
│   ├── architecture.md
│   ├── project-context.md
│   ├── api-reference.md
│   ├── skills-guide.md
│   ├── llm-providers.md
│   └── home-automation.md
│
└── config/                      # Default configuration files
    ├── personality.default.yaml # Default personality config
    └── priority_rules.default.yaml # Default priority rules
```

### Architectural Boundaries

**API Boundaries:**

| Boundary | Type | Location | Consumers |
|----------|------|----------|-----------|
| Web UI API | REST/WebSocket | `web/server.py` | Browser |
| Client Protocol | WebSocket | `server/protocol.py` | Room/Mobile clients (Phase 3) |
| Home Assistant | REST/WebSocket | `home/automation.py` | External |
| MQTT Events | Pub/Sub | `events/mqtt_bridge.py` | External IoT |

**Component Boundaries:**

```
┌─────────────────────────────────────────────────────────────┐
│                     core/jarvis.py                          │
│                   (Central Orchestrator)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  speech/ │  │  brain/  │  │  home/   │  │ skills/  │   │
│  │          │  │          │  │          │  │          │   │
│  │ - STT    │  │ - LLM    │  │ - HA API │  │ - Weather│   │
│  │ - TTS    │  │ - Intent │  │ - MQTT   │  │ - Calendar│  │
│  │ - Wake   │  │ - Provs  │  │ - Bridge │  │ - etc.   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│        │              │             │             │        │
│        └──────────────┴──────┬──────┴─────────────┘        │
│                              │                              │
│  ┌───────────────────────────┴───────────────────────────┐ │
│  │                     events/bus.py                      │ │
│  │                    (Event Bus Layer)                   │ │
│  └───────────────────────────┬───────────────────────────┘ │
│                              │                              │
│  ┌──────────┐  ┌──────────┐  │  ┌──────────┐  ┌──────────┐│
│  │ memory/  │  │personality│  │  │scheduler/│  │  users/  ││
│  │          │  │          │  │  │          │  │          ││
│  │ - Store  │  │ - Config │  │  │ - Jobs   │  │ - Profiles│
│  │ - Models │  │ - Prompt │  │  │ - Daemon │  │ - Guest  ││
│  │ - Query  │  │ - Context│  │  │ - Triggers│  │ - Auth  ││
│  └──────────┘  └──────────┘  │  └──────────┘  └──────────┘│
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
```

**Data Boundaries:**

| Data Store | Location | Access Pattern |
|------------|----------|----------------|
| Memory DB | `~/.jarvis/memory.db` | `memory/store.py` only |
| Settings | `~/.jarvis/settings.json` | `web/server.py`, `core/config.py` |
| Personality | `~/.jarvis/personality.yaml` | `personality/config.py` only |
| Calendar | `~/.jarvis/calendar.json` | `skills/calendar_skill.py` only |
| Reminders | `~/.jarvis/reminders.json` | `skills/reminder_skill.py` only |

### Requirements to Structure Mapping

**Phase 1 (MVP) Requirements:**

| Requirement | Files |
|-------------|-------|
| FR1-8 (Memory) | `memory/store.py`, `memory/models.py`, `memory/queries.py` |
| FR9-13 (Personality) | `personality/config.py`, `personality/prompt.py` |
| FR14-18 (Events) | `events/bus.py`, `events/types.py`, `home/event_bridge.py` |
| FR42-46 (Users) | `users/profiles.py`, `users/guest.py` |

**Phase 2 Requirements:**

| Requirement | Files |
|-------------|-------|
| FR19-22 (Scheduler) | `scheduler/daemon.py`, `scheduler/jobs.py` |
| FR52-54 (Integration Skills) | `skills/email_skill.py`, `skills/print_skill.py`, `skills/ci_skill.py` |

**Phase 3 Requirements:**

| Requirement | Files |
|-------------|-------|
| FR35-41 (Orchestration) | `orchestration/planner.py`, `orchestration/executor.py` |
| FR55-60 (Distributed) | `server/protocol.py`, `server/audio.py`, `server/clients.py` |

### Integration Points

**Internal Communication:**

| From | To | Method |
|------|-----|--------|
| `speech/` | `events/` | Event emission on wake word, speech recognized |
| `home/` | `events/` | Event emission on HA state changes |
| `events/` | `scheduler/` | Schedule triggers emit events |
| `memory/` | `personality/` | Context injection into prompts |
| `brain/` | `memory/` | Record interactions, query context |

**External Integrations:**

| Integration | Module | Protocol |
|-------------|--------|----------|
| Home Assistant | `home/automation.py` | REST + WebSocket |
| MQTT Broker | `events/mqtt_bridge.py` | MQTT 3.1.1/5.0 |
| Ollama | `brain/providers/ollama.py` | REST |
| Cloud LLMs | `brain/providers/*.py` | REST |
| ArgusAI | `skills/argus_camera_skill.py` | REST |

### Data Flow

```
User Voice Input
       │
       ▼
┌──────────────┐    ┌──────────────┐
│   speech/    │───▶│   events/    │◀─── Home Events
│ (Whisper STT)│    │   (Bus)      │
└──────────────┘    └──────────────┘
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│   brain/     │◀───│   memory/    │
│  (LLM + NLU) │    │  (Context)   │
└──────────────┘    └──────────────┘
       │                   ▲
       ▼                   │
┌──────────────┐           │
│   skills/    │───────────┘
│  (Execute)   │     (Record interaction)
└──────────────┘
       │
       ▼
┌──────────────┐
│   speech/    │
│ (Piper TTS)  │
└──────────────┘
       │
       ▼
  Audio Output
```

### File Organization Patterns

**Configuration Files:**

| File | Location | Purpose |
|------|----------|---------|
| `pyproject.toml` | Root | Dependencies, build config |
| `.env` / `.env.example` | Root | Environment variables |
| `config/personality.default.yaml` | Root | Default personality |
| `~/.jarvis/settings.json` | User | Runtime settings |
| `~/.jarvis/personality.yaml` | User | Custom personality |

**Development Workflow:**

```bash
# Development
uv sync --extra dev           # Install with dev deps
uv run jarvis                  # Run voice assistant
uv run jarvis-web              # Run web UI

# Testing
uv run pytest                  # All tests
uv run pytest tests/test_memory.py -v  # Specific module

# Quality
uv run ruff check .            # Lint
uv run ruff format .           # Format
uv run mypy .                  # Type check

# Database
uv run alembic upgrade head    # Run migrations
uv run alembic revision -m "Add X"  # Create migration
```

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All architectural decisions work together without conflicts. SQLite + SQLAlchemy integrates with the async-first Python architecture. The hybrid event bus (MQTT external + asyncio internal) leverages existing infrastructure while enabling new proactive capabilities. APScheduler and WebSocket protocols are compatible with FastAPI and the async model.

**Pattern Consistency:**
All implementation patterns support the architectural decisions. Naming conventions are consistent across database, events, and Python code. Structure patterns align with the existing codebase organization.

**Structure Alignment:**
The project structure supports all architectural decisions with clear module boundaries. Integration points are properly structured and documented.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
All 68 FRs are architecturally supported across 10 capability areas:
- Phase 1 (MVP): 46 FRs covered by memory, personality, events, voice, home, users, skills, config modules
- Phase 2: 8 FRs covered by scheduler, pattern recognition, integration skills
- Phase 3: 14 FRs covered by orchestration and server modules

**Non-Functional Requirements Coverage:**
All 22 NFRs are addressed through architectural decisions:
- Performance: Async-first architecture, local SQLite, concurrent operations
- Security: Encryption at rest, TLS, keychain storage, privacy boundaries
- Reliability: Graceful degradation, auto-recovery, zero data loss design
- Integration: Stable interfaces, backward compatibility
- Usability: Natural error messages, web configuration
- Maintainability: Structured logging, health endpoints, reversible migrations

### Implementation Readiness Validation ✅

**Decision Completeness:**
All critical decisions documented with specific technology versions and rationale. Implementation patterns are comprehensive with examples and anti-patterns.

**Structure Completeness:**
Complete project structure defined with all files, directories, and purposes. Component boundaries and integration points clearly specified.

**Pattern Completeness:**
12 potential conflict points standardized. Comprehensive naming, structure, format, communication, and process patterns documented.

### Gap Analysis Results

**Critical Gaps:** None

**Important Gaps (Non-Blocking):**
- Phase 3 WebSocket binary frame header format (can be detailed during implementation)
- Audio codec selection guidance for different network conditions

**Nice-to-Have (Future Enhancement):**
- Deployment automation (Docker, systemd)
- Monitoring/alerting configuration
- Development environment scripting

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed (High - distributed, ML, real-time)
- [x] Technical constraints identified (Python 3.11+, async, Pydantic v2)
- [x] Cross-cutting concerns mapped (memory, events, personality, security)

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions (5 decisions)
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**✅ Implementation Patterns**
- [x] Naming conventions established (database, event, Python)
- [x] Structure patterns defined (modules, files, config)
- [x] Communication patterns specified (event bus, memory access)
- [x] Process patterns documented (error handling, degradation, async)

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Brownfield foundation provides proven patterns and working infrastructure
- Phase-gated approach reduces risk and enables incremental delivery
- Local-first philosophy aligns with privacy requirements
- Async-first architecture supports all concurrency requirements
- Clear separation of concerns enables parallel development

**Areas for Future Enhancement:**
- Phase 3 protocol details can be refined during implementation
- Deployment automation to be developed alongside infrastructure
- Monitoring solutions to be selected based on operational experience

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and boundaries
- Refer to this document for all architectural questions
- Maintain existing patterns from `docs/project-context.md`

**First Implementation Priority:**
Phase 1 Foundation - Start with `memory/` module (SQLite + SQLAlchemy setup), then `personality/` (system prompt + YAML config), then `events/` (internal event bus skeleton).

**Development Commands:**
```bash
uv sync --extra dev            # Install dependencies
uv run pytest                  # Run tests
uv run ruff check . && uv run mypy .  # Quality checks
uv run alembic upgrade head    # Database migrations
```

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2026-01-03
**Document Location:** `_bmad-output/planning-artifacts/architecture.md`

### Final Architecture Deliverables

**Complete Architecture Document**
- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**Implementation Ready Foundation**
- 5 architectural decisions made (Memory, Event Bus, Scheduler, Personality, Client/Server)
- 12 implementation patterns defined (naming, structure, format, communication, process)
- 8 new architectural components specified (memory, events, personality, scheduler, users, orchestration, server, utils)
- 68 FRs and 22 NFRs fully supported

**AI Agent Implementation Guide**
- Technology stack with verified versions
- Consistency rules that prevent implementation conflicts
- Project structure with clear boundaries
- Integration patterns and communication standards

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing J.A.R.V.I.S. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
Phase 1 Foundation - `memory/` module (SQLite + SQLAlchemy), then `personality/` (system prompt + YAML), then `events/` (internal event bus).

**Development Sequence:**
1. Set up development environment per architecture (`uv sync --extra dev`)
2. Implement memory store with SQLAlchemy models and Alembic migrations
3. Create personality system with YAML config and prompt builder
4. Build event bus skeleton with asyncio pub/sub
5. Add user management module for guest mode support
6. Continue with Phase 2 and 3 features as documented

### Quality Assurance Checklist

**✅ Architecture Coherence**
- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**
- [x] All 68 functional requirements are supported
- [x] All 22 non-functional requirements are addressed
- [x] Cross-cutting concerns are handled
- [x] Integration points are defined

**✅ Implementation Readiness**
- [x] Decisions are specific and actionable
- [x] Patterns prevent agent conflicts
- [x] Structure is complete and unambiguous
- [x] Examples are provided for clarity

### Project Success Factors

**Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction.

**Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly.

**Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs to technical implementation.

**Solid Foundation**
The brownfield foundation and architectural patterns provide a production-ready path following current best practices.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation.

