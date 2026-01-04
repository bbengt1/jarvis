---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
project_name: 'J.A.R.V.I.S.'
date: '2026-01-03'
---

# J.A.R.V.I.S. - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for J.A.R.V.I.S., decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**Memory & Context (Phase 1)**
- FR1: System can persist user preferences, history, and relationship context across sessions
- FR2: System can recall relevant context from previous conversations when appropriate
- FR3: System can learn implicit preferences from user behavior patterns
- FR4: System can store explicit preferences when user states them
- FR5: User can view what J.A.R.V.I.S. remembers about them
- FR6: User can delete specific memories or preference data
- FR7: System can associate memories with temporal context (when things happened)
- FR8: System can prioritize recent and frequently-referenced memories over old, rarely-used ones

**Personality & Character (Phase 1)**
- FR9: System can respond with consistent personality across all interactions ("Sir", dry wit, formal but trusted peer)
- FR10: System can adapt tone based on context (e.g., more direct for urgent matters)
- FR11: System can make observations and offer unsolicited but relevant comments
- FR12: System can express opinions within appropriate boundaries
- FR13: System can maintain character consistency across different interaction modes (voice, text, web UI)

**Event Awareness & Proactivity (Phase 1-2)**
- FR14: System can receive and process events from home automation systems
- FR15: System can announce relevant events to the user without being asked
- FR16: System can filter events based on user-defined priority rules
- FR17: System can determine appropriate timing for event announcements
- FR18: System can correlate multiple events into meaningful summaries
- FR19: System can detect patterns in events and learn from them (Phase 2)
- FR20: System can initiate conversations based on scheduled triggers (Phase 2)
- FR21: System can deliver synthesized morning briefings (Phase 2)
- FR22: System can manage evening transition with day summary (Phase 2)

**Voice Interaction (Phase 1)**
- FR23: System can detect wake word and activate listening
- FR24: System can transcribe spoken commands using speech recognition
- FR25: System can respond with synthesized speech
- FR26: User can interrupt J.A.R.V.I.S. during speech playback
- FR27: System can handle multi-turn conversations with context
- FR28: System can operate in hands-free mode continuously

**Home Automation Integration (Phase 1)**
- FR29: System can control smart home devices (lights, locks, climate, media, covers)
- FR30: System can query device states and report to user
- FR31: System can execute scenes and automations by name
- FR32: System can suggest appropriate automations based on context
- FR33: System can coordinate multiple device actions atomically
- FR34: System can receive real-time state updates from home automation

**Orchestration & Planning (Phase 3)**
- FR35: System can break down high-level requests into multiple actions
- FR36: System can create plans that span multiple systems (calendar, home, shopping)
- FR37: System can present plans for user approval before execution
- FR38: System can execute approved plans autonomously
- FR39: System can learn from plan corrections and improve future suggestions
- FR40: System can act autonomously within user-defined boundaries
- FR41: System can inform user of autonomous actions taken

**User & Guest Management (Phase 1)**
- FR42: System can recognize the primary user
- FR43: System can interact with household guests in simplified mode
- FR44: Guest interactions are not stored in relationship memory
- FR45: System can adapt personality for different recognized individuals
- FR46: System can limit guest access to appropriate functionality

**Skills & Integration (Phase 1-2)**
- FR47: User can invoke built-in skills (weather, calendar, reminders, time)
- FR48: System can provide weather information for configured location
- FR49: System can manage calendar events (view, create, modify)
- FR50: System can set and manage reminders with notifications
- FR51: System can query ArgusAI camera system for security events
- FR52: System can integrate with email for triage and summaries (Phase 2)
- FR53: System can monitor 3D print status (Phase 2)
- FR54: System can check CI/CD pipeline status (Phase 2)

**Distributed Presence (Phase 3)**
- FR55: System can receive input from multiple room clients
- FR56: System can route audio output to appropriate room client
- FR57: System can maintain conversation context across room transitions
- FR58: System can detect user presence in rooms
- FR59: System can hand off active conversation between clients seamlessly
- FR60: Mobile client can connect to system remotely

**Configuration & Administration (Phase 1)**
- FR61: User can configure system settings via web interface
- FR62: User can switch between LLM providers at runtime
- FR63: User can manage API keys and credentials securely
- FR64: User can configure skill-specific settings
- FR65: User can define priority rules for event interruptions
- FR66: User can add new skills without modifying core code
- FR67: User can view system logs and diagnostic information
- FR68: User can backup and restore system configuration and memory

### Non-Functional Requirements

**Performance**
- NFR1: Voice response latency <2 seconds, wake word <500ms, TTS <1 second
- NFR2: Memory preference retrieval <100ms, context search <500ms
- NFR3: Event processing <1 second, announcements <2 seconds
- NFR4: Concurrent audio input, LLM generation, and TTS without blocking

**Security**
- NFR5: AES-256 encryption at rest, keychain for credentials, no audio persistence
- NFR6: TLS 1.3 for all communication, HTTPS for web UI, pre-shared keys for clients
- NFR7: Guest privacy (no memory storage), opt-in cloud LLM, viewable/deletable data
- NFR8: Web UI authentication, mobile biometric/PIN, limited guest access

**Reliability**
- NFR9: 99% uptime for voice interaction, announced downtime, auto-recovery
- NFR10: Graceful degradation (cloud→local LLM, offline mode, stateless fallback)
- NFR11: Survive unexpected shutdown, immediate config persistence, daily backup
- NFR12: Graceful error recovery for voice, LLM timeouts, HA failures

**Integration**
- NFR13: Home Assistant 2024.1+ REST API, persistent WebSocket
- NFR14: Ollama, OpenAI, Anthropic, Google, xAI providers; switching <5 seconds
- NFR15: MQTT 3.1.1/5.0, auto-reconnection, QoS 0/1/2
- NFR16: New skills without core changes, stable skill interface, skill-specific config

**Usability**
- NFR17: <5% false wake rate, 95% speech accuracy, clear TTS
- NFR18: Web UI for all settings, voice for critical settings, no restart required
- NFR19: Natural language errors, remediation suggestions, TTS error announcements

**Maintainability**
- NFR20: Structured logging with timestamps, configurable levels, rotation
- NFR21: Web UI health dashboard, integration status, memory statistics
- NFR22: Rolling updates, automatic reversible migrations, backward compatible config

### Additional Requirements from Architecture

**Brownfield Foundation (No Starter Template)**
- This is a brownfield project - no initialization needed, extend existing codebase
- Preserve existing async-first patterns, lazy loading, provider pattern, skill registry

**Phase 1 Infrastructure**
- Memory Store: SQLite + SQLAlchemy 2.x at `~/.jarvis/memory.db` with Alembic migrations
- Personality System: YAML config at `~/.jarvis/personality.yaml` with system prompt template
- Event Bus: MQTT (external) + asyncio pub/sub (internal) with EventType StrEnum
- User Management: Primary user recognition, guest mode with privacy isolation

**Phase 2 Infrastructure**
- Scheduler Daemon: APScheduler 4.x with AsyncIOExecutor, SQLite job store
- Pattern Recognition: Confidence scoring, behavior analysis from history
- Integration Skills: Email triage, 3D print monitoring, CI/CD status

**Phase 3 Infrastructure**
- Client/Server Protocol: WebSocket with binary audio (PCM/Opus) + JSON commands
- Orchestration Module: Multi-step planner, plan approval workflow, autonomous execution
- Distributed Presence: Room clients, mobile client, seamless handoff

**Database Schema Requirements**
- Tables: `user_preferences`, `conversation_history`, `learned_patterns`, `relationships`
- Naming: plural snake_case tables, snake_case columns, UTC timestamps
- All models use SQLAlchemy 2.x async with `Mapped` type hints

**Event Architecture Requirements**
- Internal: asyncio pub/sub with typed Event dataclass
- External: MQTT topics under `jarvis/events/#` and `jarvis/commands/#`
- Event types: wake_word_detected, speech_recognized, response_generated, home_event, schedule_triggered, memory_updated

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1-FR8 | Epic 1 | Memory persistence, recall, preferences, temporal context |
| FR9-FR13 | Epic 2 | Personality, tone, wit, opinions, consistency |
| FR14-FR18 | Epic 3 | Event processing, announcements, filtering, timing |
| FR19-FR22 | Epic 5 | Pattern detection, scheduled triggers, briefings |
| FR23-FR28 | *Existing* | Voice interaction (already implemented) |
| FR29-FR34 | *Existing* | Home automation (already implemented) |
| FR35-FR41 | Epic 7 | Orchestration, planning, autonomy |
| FR42-FR46 | Epic 1 | User recognition, guest mode, privacy |
| FR47-FR51 | *Existing* | Skills - weather, calendar, reminders (already implemented) |
| FR52-FR54 | Epic 6 | Email, 3D print, CI/CD skills |
| FR55-FR60 | Epic 8 | Distributed presence, room clients, mobile |
| FR61-FR68 | Epic 4 | Configuration, credentials, backup, logging |

## Epic List

### Epic 1: Memory & Identity
**Goal:** J.A.R.V.I.S. remembers who you are, your preferences, and your history - building the foundation for a genuine relationship.

**User Outcome:** After this epic, J.A.R.V.I.S. will remember your preferences, recall relevant context from past conversations, recognize you vs guests, and maintain privacy boundaries.

**FRs Covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR42, FR43, FR44, FR45, FR46
**Phase:** 1 (MVP)

---

### Epic 2: J.A.R.V.I.S. Personality
**Goal:** J.A.R.V.I.S. develops his signature personality - the formal "Sir", dry wit, and trusted peer dynamic that defines the Iron Man AI.

**User Outcome:** After this epic, J.A.R.V.I.S. will respond with consistent character, adapt tone to context, make observations, express opinions, and maintain personality across all interaction modes.

**FRs Covered:** FR9, FR10, FR11, FR12, FR13
**Phase:** 1 (MVP)

---

### Epic 3: Event Awareness & Proactivity
**Goal:** J.A.R.V.I.S. becomes proactive - announcing relevant events, filtering by priority, and timing interruptions appropriately.

**User Outcome:** After this epic, J.A.R.V.I.S. will announce doorbell rings, package deliveries, and home events without being asked, respecting your priority rules and timing preferences.

**FRs Covered:** FR14, FR15, FR16, FR17, FR18
**Phase:** 1 (MVP)

---

### Epic 4: Configuration & Administration
**Goal:** Users can configure new J.A.R.V.I.S. capabilities, manage credentials securely, and maintain system health.

**User Outcome:** After this epic, users can configure priority rules, manage memory settings, view logs, backup/restore, and control all new features via the web UI.

**FRs Covered:** FR61, FR62, FR63, FR64, FR65, FR66, FR67, FR68
**Phase:** 1 (MVP)

---

### Epic 5: Scheduled Intelligence
**Goal:** J.A.R.V.I.S. becomes time-aware - delivering morning briefings, evening summaries, and detecting behavioral patterns.

**User Outcome:** After this epic, J.A.R.V.I.S. will greet you with a synthesized morning briefing, manage evening transitions, learn your patterns, and initiate conversations at appropriate times.

**FRs Covered:** FR19, FR20, FR21, FR22
**Phase:** 2

---

### Epic 6: Extended Skills
**Goal:** J.A.R.V.I.S. gains new capabilities - email triage, 3D print monitoring, and CI/CD pipeline status.

**User Outcome:** After this epic, users can ask J.A.R.V.I.S. to triage email, check on 3D print progress, and get CI/CD build status - extending the overnight work capabilities.

**FRs Covered:** FR52, FR53, FR54
**Phase:** 2

---

### Epic 7: Orchestration & Autonomy
**Goal:** J.A.R.V.I.S. can "figure it out" - breaking down complex requests, creating multi-system plans, and acting autonomously within boundaries.

**User Outcome:** After this epic, users can give high-level instructions like "I'm having 8 people over Saturday" and J.A.R.V.I.S. will plan, confirm, and execute across calendar, home, and other systems.

**FRs Covered:** FR35, FR36, FR37, FR38, FR39, FR40, FR41
**Phase:** 3

---

### Epic 8: Distributed Presence
**Goal:** J.A.R.V.I.S. is everywhere - room clients throughout the house and mobile access on the go.

**User Outcome:** After this epic, users can interact with J.A.R.V.I.S. from any room, seamlessly hand off conversations, and connect remotely via mobile.

**FRs Covered:** FR55, FR56, FR57, FR58, FR59, FR60
**Phase:** 3

---

## Epic 1: Memory & Identity

**Goal:** J.A.R.V.I.S. remembers who you are, your preferences, and your history - building the foundation for a genuine relationship.

### Story 1.1: Initialize Memory Store

As a **developer**,
I want **the memory store infrastructure set up with SQLite, SQLAlchemy, and Alembic**,
So that **all memory-related features have a reliable persistence layer**.

**Acceptance Criteria:**

**Given** the J.A.R.V.I.S. system starts for the first time
**When** the memory module initializes
**Then** a SQLite database is created at `~/.jarvis/memory.db`
**And** the database schema is applied via Alembic migrations
**And** the following tables exist: `user_preferences`, `conversation_history`, `learned_patterns`

**Given** the memory database already exists
**When** the system starts
**Then** pending Alembic migrations are applied automatically
**And** existing data is preserved

**Given** a database operation is performed
**When** the operation uses the MemoryStore interface
**Then** all operations use async SQLAlchemy sessions
**And** operations complete within NFR2 latency requirements (<100ms for preferences)

---

### Story 1.2: Persist User Preferences

As a **user**,
I want **J.A.R.V.I.S. to remember my explicit preferences when I state them**,
So that **I don't have to repeat myself**.

**Acceptance Criteria:**

**Given** I tell J.A.R.V.I.S. "I prefer the temperature at 72 degrees"
**When** J.A.R.V.I.S. processes this statement
**Then** the preference is stored in the `user_preferences` table
**And** J.A.R.V.I.S. confirms "I'll remember that, Sir"

**Given** a preference already exists for a key
**When** I state a new value for that preference
**Then** the existing preference is updated
**And** the `updated_at` timestamp is set

**Given** I ask "What temperature do I prefer?"
**When** J.A.R.V.I.S. processes the query
**Then** J.A.R.V.I.S. retrieves and responds with the stored preference
**And** retrieval completes within 100ms

---

### Story 1.3: Record Interaction History

As a **user**,
I want **J.A.R.V.I.S. to record our conversations with context**,
So that **he can reference past interactions naturally**.

**Acceptance Criteria:**

**Given** I have a conversation with J.A.R.V.I.S.
**When** each exchange completes
**Then** the interaction is recorded in `conversation_history`
**And** the record includes: user text, assistant response, timestamp (UTC), and context metadata

**Given** an interaction involves a skill
**When** the interaction is recorded
**Then** the context metadata includes the skill name and relevant entities

**Given** multiple interactions occur
**When** the system queries history
**Then** interactions are retrievable by time range
**And** interactions are retrievable by keyword/entity search

---

### Story 1.4: Recall Relevant Context

As a **user**,
I want **J.A.R.V.I.S. to recall relevant context from previous conversations**,
So that **our interactions feel continuous and relationship-like**.

**Acceptance Criteria:**

**Given** I previously discussed a topic with J.A.R.V.I.S.
**When** I mention that topic again
**Then** J.A.R.V.I.S. retrieves relevant past interactions
**And** context is injected into the LLM prompt

**Given** multiple past interactions exist
**When** the system queries for relevant context
**Then** recent interactions are weighted higher than old ones
**And** frequently-referenced memories are prioritized (FR8)
**And** query completes within 500ms (NFR2)

**Given** I ask "What did I say about X last week?"
**When** J.A.R.V.I.S. processes the query
**Then** temporal context is used to filter results (FR7)
**And** J.A.R.V.I.S. summarizes the relevant past discussion

---

### Story 1.5: Learn Implicit Preferences

As a **user**,
I want **J.A.R.V.I.S. to learn my preferences from my behavior patterns**,
So that **he anticipates my needs without me stating them explicitly**.

**Acceptance Criteria:**

**Given** I consistently perform certain actions (e.g., turn on office lights at 8am)
**When** the pattern detection runs (scheduled or on-demand)
**Then** the pattern is identified and stored in `learned_patterns`
**And** the pattern includes confidence score, frequency, and conditions

**Given** a learned pattern has high confidence
**When** the triggering conditions occur
**Then** J.A.R.V.I.S. can reference this pattern for suggestions
**And** the pattern is available to the personality system

**Given** my behavior changes over time
**When** patterns are re-analyzed
**Then** stale patterns decrease in confidence
**And** new patterns can supersede old ones

---

### Story 1.6: Memory Management Interface

As a **user**,
I want **to view and delete what J.A.R.V.I.S. remembers about me**,
So that **I maintain control over my personal data**.

**Acceptance Criteria:**

**Given** I ask "What do you remember about me?"
**When** J.A.R.V.I.S. processes the request
**Then** J.A.R.V.I.S. summarizes stored preferences, recent interactions, and learned patterns
**And** the response is organized by category

**Given** I say "Forget that I prefer 72 degrees"
**When** J.A.R.V.I.S. processes the request
**Then** the specific preference is deleted from storage
**And** J.A.R.V.I.S. confirms "Done, Sir. I've forgotten that preference."

**Given** I say "Clear all my data"
**When** J.A.R.V.I.S. processes the request
**Then** J.A.R.V.I.S. asks for confirmation before proceeding
**And** upon confirmation, all user data is deleted
**And** the system returns to a clean state

---

### Story 1.7: User Recognition

As a **user**,
I want **J.A.R.V.I.S. to recognize me as the primary user**,
So that **he personalizes interactions and applies my preferences**.

**Acceptance Criteria:**

**Given** the system is configured with a primary user
**When** the primary user interacts with J.A.R.V.I.S.
**Then** the system applies the user's stored preferences
**And** the personality system uses full relationship context

**Given** different recognized users exist (future: voice profiles)
**When** a recognized user interacts
**Then** the system can adapt personality traits per user (FR45)
**And** separate preference stores can be maintained per user

**Given** an unrecognized voice is detected
**When** the system cannot identify the speaker
**Then** the system defaults to guest mode (Story 1.8)

---

### Story 1.8: Guest Mode

As a **household guest**,
I want **to interact with J.A.R.V.I.S. in a simplified mode**,
So that **I can use basic features without affecting the owner's data**.

**Acceptance Criteria:**

**Given** a guest interacts with J.A.R.V.I.S.
**When** J.A.R.V.I.S. is in guest mode
**Then** interactions are NOT stored in relationship memory (FR44)
**And** the session is treated as ephemeral

**Given** a guest requests functionality
**When** the request is for a protected feature (e.g., view owner's calendar)
**Then** access is denied with a polite explanation (FR46)
**And** only predefined guest-allowed features are accessible

**Given** a guest asks a general question
**When** J.A.R.V.I.S. responds
**Then** the personality remains consistent but formal
**And** personal relationship context is not referenced

---

## Epic 2: J.A.R.V.I.S. Personality

**Goal:** J.A.R.V.I.S. develops his signature personality - the formal "Sir", dry wit, and trusted peer dynamic that defines the Iron Man AI.

### Story 2.1: Personality Configuration System

As a **user**,
I want **J.A.R.V.I.S.'s personality to be configurable via YAML**,
So that **I can tune his character traits without code changes**.

**Acceptance Criteria:**

**Given** the system starts
**When** the personality module initializes
**Then** it loads configuration from `~/.jarvis/personality.yaml`
**And** if the file doesn't exist, a default is created

**Given** the personality config exists
**When** it is loaded
**Then** the following traits are available: `formality`, `wit`, `verbosity`, `proactivity`
**And** character settings are available: `name`, `address_user_as`
**And** boundary settings are available: `opinions`, `pushback`, `humor`

**Given** I modify the personality config
**When** the system reloads (or restarts)
**Then** the new personality settings take effect
**And** J.A.R.V.I.S. reflects the updated traits

---

### Story 2.2: System Prompt Builder

As a **developer**,
I want **a dynamic system prompt built from personality config and memory context**,
So that **J.A.R.V.I.S. maintains consistent character with personalized context**.

**Acceptance Criteria:**

**Given** a conversation starts
**When** the LLM is invoked
**Then** a system prompt is constructed from the personality template
**And** the template includes character traits from config
**And** dynamic context from memory is injected

**Given** different LLM providers are used
**When** the system prompt is generated
**Then** it works consistently across all providers (FR13)
**And** no provider-specific fine-tuning is required

**Given** the memory store has relevant context
**When** the system prompt is built
**Then** recent preferences and patterns are included
**And** the prompt remains within reasonable token limits

---

### Story 2.3: Context-Aware Tone Adaptation

As a **user**,
I want **J.A.R.V.I.S. to adapt his tone based on context**,
So that **he's more direct for urgent matters and relaxed for casual conversation**.

**Acceptance Criteria:**

**Given** I report an urgent situation (e.g., "There's smoke in the kitchen!")
**When** J.A.R.V.I.S. responds
**Then** the response is more direct and concise
**And** unnecessary wit is suppressed
**And** action-oriented language is used

**Given** I'm having a casual conversation
**When** J.A.R.V.I.S. responds
**Then** the full personality is expressed
**And** wit and observations are included per config settings

**Given** the time of day or detected context changes
**When** J.A.R.V.I.S. responds
**Then** tone may adapt (e.g., calmer late at night)
**And** the core character remains consistent

---

### Story 2.4: Proactive Observations

As a **user**,
I want **J.A.R.V.I.S. to make observations and offer unsolicited but relevant comments**,
So that **he feels like a thoughtful companion rather than a passive tool**.

**Acceptance Criteria:**

**Given** J.A.R.V.I.S. notices something relevant during an interaction
**When** the observation is contextually appropriate
**Then** J.A.R.V.I.S. may add a brief observation to his response
**And** observations are in character (dry wit, not intrusive)

**Given** the `proactivity` trait is set low
**When** J.A.R.V.I.S. considers making an observation
**Then** observations are suppressed or minimized

**Given** an observation has been made recently
**When** J.A.R.V.I.S. considers another
**Then** frequency is limited to avoid being annoying
**And** only high-value observations are shared

---

### Story 2.5: Opinion Expression

As a **user**,
I want **J.A.R.V.I.S. to express opinions within appropriate boundaries**,
So that **he feels like a trusted peer with his own perspective**.

**Acceptance Criteria:**

**Given** the `opinions` boundary is enabled in config
**When** I ask J.A.R.V.I.S. for his opinion
**Then** he provides a thoughtful perspective
**And** the opinion is expressed with appropriate hedging ("If I may, Sir...")

**Given** the `pushback` boundary is enabled
**When** I propose something J.A.R.V.I.S. considers inadvisable
**Then** he may respectfully disagree or suggest alternatives
**And** pushback is never hostile or condescending

**Given** boundaries restrict opinion expression
**When** J.A.R.V.I.S. would normally opine
**Then** he defers to the user's judgment
**And** he may note he's withholding opinion if appropriate

---

## Epic 3: Event Awareness & Proactivity

**Goal:** J.A.R.V.I.S. becomes aware of his environment and can proactively communicate important events to the user.

### Story 3.1: Internal Event Bus

As a **developer**,
I want **an internal asyncio-based event bus for component communication**,
So that **system components can publish and subscribe to events without tight coupling**.

**Acceptance Criteria:**

**Given** the event bus is initialized
**When** a component subscribes to an event type
**Then** the subscription is registered with the handler
**And** multiple handlers can subscribe to the same event type

**Given** a component publishes an event
**When** the event is emitted
**Then** all subscribed handlers are invoked asynchronously
**And** handlers receive the typed Event object with timestamp, type, payload, and source

**Given** the EventType enum is defined
**When** new event types are needed
**Then** they can be added to the enum (e.g., WAKE_WORD_DETECTED, SPEECH_RECOGNIZED, HOME_EVENT, MEMORY_UPDATED)
**And** events are strongly typed with dataclass structure

---

### Story 3.2: Home Automation Event Bridge

As a **user**,
I want **J.A.R.V.I.S. to receive events from Home Assistant via MQTT**,
So that **he knows what's happening in my home in real-time**.

**Acceptance Criteria:**

**Given** MQTT is configured with broker URL
**When** the system starts
**Then** it connects to the MQTT broker
**And** subscribes to Home Assistant state change topics

**Given** a Home Assistant state change occurs
**When** the MQTT message is received
**Then** it is transformed into an internal Event
**And** published to the internal event bus as EventType.HOME_EVENT
**And** the payload includes entity_id, old_state, new_state, and attributes

**Given** MQTT connection is lost
**When** reconnection is attempted
**Then** the system uses exponential backoff
**And** events are not lost during brief disconnections (if QoS allows)

---

### Story 3.3: Event Priority Rules

As a **user**,
I want **to configure which events are important to me**,
So that **J.A.R.V.I.S. only announces things I care about**.

**Acceptance Criteria:**

**Given** I configure priority rules in settings
**When** an event is received
**Then** it is evaluated against the rules
**And** matched events are marked with priority (high, normal, low, ignore)

**Given** a rule matches entity patterns (e.g., "door.*", "motion.front_*")
**When** events from matching entities arrive
**Then** the rule's priority is applied

**Given** no rule matches an event
**When** the event is processed
**Then** a default priority is applied (configurable)
**And** ignored events are not announced but may be logged

---

### Story 3.4: Event Announcement System

As a **user**,
I want **J.A.R.V.I.S. to announce important events via TTS**,
So that **I'm informed without checking screens**.

**Acceptance Criteria:**

**Given** an event is marked as high or normal priority
**When** announcement conditions are met
**Then** J.A.R.V.I.S. generates a natural language description
**And** speaks it via TTS with appropriate personality

**Given** the user is in a conversation with J.A.R.V.I.S.
**When** an event needs announcing
**Then** the announcement waits for a natural pause
**Or** is integrated into the response if contextually relevant

**Given** multiple events arrive in quick succession
**When** they would trigger announcements
**Then** they may be batched or summarized
**And** the user isn't overwhelmed with rapid-fire announcements

---

### Story 3.5: Event Timing Intelligence

As a **user**,
I want **J.A.R.V.I.S. to choose appropriate times for announcements**,
So that **I'm not disturbed at inappropriate moments**.

**Acceptance Criteria:**

**Given** quiet hours are configured (e.g., 10pm - 7am)
**When** events occur during quiet hours
**Then** only high-priority events are announced
**And** normal events are queued or logged silently

**Given** the system detects I'm sleeping (no activity, night mode)
**When** non-critical events occur
**Then** they are suppressed until I'm active

**Given** I'm actively interacting with J.A.R.V.I.S.
**When** he needs to announce something
**Then** the timing is adjusted to not interrupt my question/response
**And** natural conversational flow is maintained

---

### Story 3.6: Event Correlation

As a **user**,
I want **J.A.R.V.I.S. to correlate related events into meaningful summaries**,
So that **I get insights rather than raw event floods**.

**Acceptance Criteria:**

**Given** multiple related events occur within a time window
**When** they are processed for announcement
**Then** J.A.R.V.I.S. may summarize (e.g., "Multiple motion sensors triggered in the front yard")
**And** the summary conveys the pattern, not each individual event

**Given** events form a logical sequence (e.g., door opens, motion detected, lights on)
**When** they are correlated
**Then** J.A.R.V.I.S. may describe the narrative ("Someone entered through the front door")
**And** speculation is clearly marked as inference

**Given** correlation is uncertain
**When** J.A.R.V.I.S. reports
**Then** he uses hedging language ("It appears..." / "I believe...")
**And** raw events can be queried if the user wants details

---

## Epic 4: Configuration & Administration

**Goal:** Administrators and users can configure all aspects of J.A.R.V.I.S. through a unified web interface with proper user management.

### Story 4.1: Unified Settings Management

As a **user**,
I want **all configuration consolidated in SQLite with JSON storage**,
So that **settings persist reliably and are accessible to all components**.

**Acceptance Criteria:**

**Given** settings were previously in settings.json
**When** the system is upgraded
**Then** settings are migrated to SQLite
**And** the JSON file is backed up but no longer primary

**Given** a component needs a setting
**When** it requests the value
**Then** it retrieves from SettingsStore (not direct file access)
**And** defaults are applied if no value exists

**Given** settings are updated
**When** they are saved
**Then** they are persisted to SQLite immediately
**And** an event is emitted for components to react to changes

---

### Story 4.2: Enhanced Web Configuration UI

As a **user**,
I want **the web UI to expose all configurable settings**,
So that **I can manage J.A.R.V.I.S. without editing files**.

**Acceptance Criteria:**

**Given** I access the web UI settings page
**When** it loads
**Then** all settings categories are displayed (General, LLM, Speech, Vision, Home, Memory, Events, Personality)
**And** current values are pre-populated from the database

**Given** I modify a setting
**When** I save changes
**Then** the setting is persisted via the API
**And** the affected component receives the update event

**Given** I enter an invalid value
**When** I attempt to save
**Then** validation feedback is shown
**And** the invalid change is rejected

---

### Story 4.3: User Profile System

As a **household member**,
I want **to have my own user profile**,
So that **J.A.R.V.I.S. recognizes me and applies my preferences**.

**Acceptance Criteria:**

**Given** the system supports multiple users
**When** a user is created
**Then** a profile is stored with name, preferences, and access level

**Given** J.A.R.V.I.S. identifies who is speaking (via voice recognition or context)
**When** responding
**Then** user-specific preferences are applied
**And** the appropriate address is used (if configured per-user)

**Given** a user doesn't identify themselves
**When** they interact
**Then** guest mode is used with default settings
**And** no personal memories are created

---

### Story 4.4: Access Control & Permissions

As an **administrator**,
I want **to control what different users can access**,
So that **guests can't modify security settings or access sensitive data**.

**Acceptance Criteria:**

**Given** users have access levels (admin, user, guest)
**When** a request is made
**Then** the access level is checked against the required permission

**Given** a guest attempts to change settings
**When** the action is blocked
**Then** J.A.R.V.I.S. explains politely that the action requires higher permissions

**Given** an admin is authenticated
**When** they access the web UI
**Then** all administrative functions are available
**And** sensitive operations may require re-authentication

---

### Story 4.5: Settings Import/Export

As an **administrator**,
I want **to export and import all configuration**,
So that **I can backup, restore, or migrate my J.A.R.V.I.S. setup**.

**Acceptance Criteria:**

**Given** I request a configuration export
**When** the export is generated
**Then** all settings are serialized to JSON
**And** sensitive values (API keys) are optionally excluded or masked

**Given** I have a configuration backup
**When** I import it
**Then** settings are merged or replaced (per my choice)
**And** the system validates the import before applying

**Given** I'm migrating to a new installation
**When** I import my backup
**Then** J.A.R.V.I.S. behaves identically to the previous installation
**And** memories and preferences are preserved

---

## Epic 5: Scheduled Intelligence

**Goal:** J.A.R.V.I.S. operates on schedules - delivering briefings, managing routines, and proactively engaging based on time and context. (Phase 2)

### Story 5.1: APScheduler Integration

As a **developer**,
I want **APScheduler 4.x integrated for persistent job scheduling**,
So that **scheduled tasks survive restarts and run reliably**.

**Acceptance Criteria:**

**Given** the scheduler module is initialized
**When** the system starts
**Then** APScheduler starts with SQLite job store
**And** previously scheduled jobs are restored

**Given** a job is scheduled
**When** its trigger time arrives
**Then** the job executes asynchronously
**And** failures are logged without crashing the scheduler

**Given** the system shuts down
**When** it restarts
**Then** missed jobs are handled per configuration (run immediately or skip)
**And** the job store maintains integrity

---

### Story 5.2: Morning Briefing

As a **user**,
I want **J.A.R.V.I.S. to deliver a synthesized morning briefing**,
So that **I start my day informed without asking for each piece**.

**Acceptance Criteria:**

**Given** morning briefing is enabled and time is configured
**When** the scheduled time arrives
**Then** J.A.R.V.I.S. gathers: weather, calendar, reminders, overnight events
**And** synthesizes a coherent briefing with personality
**And** delivers via TTS

**Given** I'm not detected as awake/present
**When** briefing time arrives
**Then** it waits for activity detection before delivering
**Or** is deferred with a note ("Your briefing from this morning, Sir...")

**Given** I interrupt the briefing
**When** I speak
**Then** J.A.R.V.I.S. pauses and responds to my query
**And** offers to continue the briefing afterward

---

### Story 5.3: Evening Transition

As a **user**,
I want **J.A.R.V.I.S. to manage evening transition with day summary**,
So that **I can wind down with a recap and preparation for tomorrow**.

**Acceptance Criteria:**

**Given** evening transition is enabled
**When** the configured time arrives
**Then** J.A.R.V.I.S. summarizes: completed tasks, pending reminders, notable events
**And** previews tomorrow's calendar
**And** offers to set any final reminders

**Given** I have undone tasks or reminders
**When** the summary is delivered
**Then** J.A.R.V.I.S. asks about deferral or completion
**And** updates accordingly

**Given** evening mode is triggered
**When** other automations are configured (lights dim, etc.)
**Then** J.A.R.V.I.S. may coordinate with home automation
**And** the transition feels cohesive

---

### Story 5.4: Recurring Scheduled Tasks

As a **user**,
I want **to create recurring scheduled tasks via voice or web UI**,
So that **J.A.R.V.I.S. handles routine check-ins and reminders automatically**.

**Acceptance Criteria:**

**Given** I say "Remind me every Monday at 9am to..."
**When** the intent is parsed
**Then** a recurring job is created in APScheduler
**And** confirmation includes the schedule pattern

**Given** I configure a recurring task in the web UI
**When** I save it
**Then** the job is persisted to the scheduler
**And** I can view, edit, or delete scheduled tasks

**Given** a recurring task executes
**When** it runs
**Then** J.A.R.V.I.S. announces or acts per the task definition
**And** execution is logged for review

---

### Story 5.5: Schedule-Triggered Conversations

As a **user**,
I want **J.A.R.V.I.S. to initiate conversations based on scheduled triggers**,
So that **he proactively checks in rather than waiting for me to ask**.

**Acceptance Criteria:**

**Given** a check-in is scheduled (e.g., "Ask about project status at 3pm")
**When** the time arrives
**Then** J.A.R.V.I.S. initiates: "Sir, I wanted to check in about [topic]..."
**And** waits for response before continuing

**Given** I don't respond to a check-in
**When** timeout occurs
**Then** J.A.R.V.I.S. notes it was attempted
**And** may retry once or defer based on configuration

**Given** context has changed (task completed, situation resolved)
**When** the check-in would trigger
**Then** J.A.R.V.I.S. may adapt or skip ("I was going to ask about X, but I see you've already...")

---

## Epic 6: Extended Skills

**Goal:** J.A.R.V.I.S. gains new capabilities through integrated research and enhanced calendar features. (Phase 2)

### Story 6.1: Web Research Skill

As a **user**,
I want **J.A.R.V.I.S. to research topics on the web for me**,
So that **I can get summarized answers without browsing myself**.

**Acceptance Criteria:**

**Given** I ask J.A.R.V.I.S. to research something
**When** the research skill is invoked
**Then** J.A.R.V.I.S. searches the web using configured search provider
**And** fetches and summarizes relevant content
**And** presents a synthesized answer with sources

**Given** research is in progress
**When** it takes more than a few seconds
**Then** J.A.R.V.I.S. provides progress feedback ("Looking into that, Sir...")
**And** results are cached for follow-up questions

**Given** I ask follow-up questions about the research
**When** context is available
**Then** J.A.R.V.I.S. uses the cached research
**And** can dig deeper on specific aspects

---

### Story 6.2: Calendar Integration Enhancement

As a **user**,
I want **J.A.R.V.I.S. to integrate with external calendars (Google, iCloud)**,
So that **my schedule is always current and synchronized**.

**Acceptance Criteria:**

**Given** I configure calendar integration
**When** credentials are provided
**Then** J.A.R.V.I.S. syncs with the external calendar
**And** events appear in the local calendar store

**Given** I create an event via J.A.R.V.I.S.
**When** the event is saved
**Then** it syncs to the external calendar
**And** confirmation includes sync status

**Given** an external calendar changes
**When** J.A.R.V.I.S. syncs (periodic or on-demand)
**Then** local calendar reflects the changes
**And** conflicts are handled gracefully (external wins by default)

---

### Story 6.3: Note-Taking Skill

As a **user**,
I want **J.A.R.V.I.S. to take and organize notes for me**,
So that **I can capture thoughts without interrupting my flow**.

**Acceptance Criteria:**

**Given** I say "Take a note: [content]"
**When** the note skill activates
**Then** the note is stored with timestamp and optional category
**And** J.A.R.V.I.S. confirms: "Noted, Sir."

**Given** I ask to review notes
**When** J.A.R.V.I.S. retrieves them
**Then** notes are presented by recency or category
**And** I can ask to delete or modify notes

**Given** notes contain actionable items
**When** reviewing
**Then** J.A.R.V.I.S. may suggest converting to reminders or tasks
**And** the user decides whether to convert

---

## Epic 7: Orchestration & Autonomy

**Goal:** J.A.R.V.I.S. can handle complex multi-step tasks autonomously, planning and executing with minimal user intervention. (Phase 3)

### Story 7.1: Multi-Step Task Planner

As a **user**,
I want **J.A.R.V.I.S. to break complex requests into executable steps**,
So that **I can give high-level instructions and trust him to figure out the details**.

**Acceptance Criteria:**

**Given** I give a complex instruction (e.g., "Prepare the house for movie night")
**When** the orchestrator receives it
**Then** it generates a plan with discrete steps
**And** presents the plan for approval or proceeds if confidence is high

**Given** a plan is generated
**When** it includes multiple skills/actions
**Then** dependencies between steps are identified
**And** parallel-safe steps are marked for concurrent execution

**Given** I approve a plan
**When** execution begins
**Then** each step is executed in order
**And** progress is reported naturally ("Dimming lights... Setting thermostat...")

---

### Story 7.2: Autonomous Execution Engine

As a **user**,
I want **J.A.R.V.I.S. to execute approved plans without constant confirmation**,
So that **tasks complete efficiently while I focus on other things**.

**Acceptance Criteria:**

**Given** a plan is approved
**When** the engine executes
**Then** each step runs in sequence (or parallel where safe)
**And** the engine handles minor errors with retries

**Given** a step fails after retries
**When** recovery isn't automatic
**Then** J.A.R.V.I.S. pauses and asks for guidance
**And** the plan state is preserved for resumption

**Given** execution completes
**When** all steps succeed
**Then** J.A.R.V.I.S. summarizes: "Movie night is ready, Sir. Lights dimmed, thermostat set to 72."
**And** the plan is logged for reference

---

### Story 7.3: Plan Persistence & Recovery

As a **user**,
I want **in-progress plans to survive interruptions**,
So that **J.A.R.V.I.S. can resume complex tasks after restarts or failures**.

**Acceptance Criteria:**

**Given** a plan is in progress
**When** the system restarts unexpectedly
**Then** the plan state is recovered from the database
**And** J.A.R.V.I.S. offers to resume: "Sir, we were preparing movie night. Shall I continue?"

**Given** a plan is paused for user input
**When** the user returns later
**Then** J.A.R.V.I.S. remembers the pending plan
**And** context is preserved for seamless continuation

**Given** a plan is no longer relevant
**When** I cancel it
**Then** rollback actions are offered if applicable
**And** the plan is archived, not deleted

---

### Story 7.4: Confidence-Based Autonomy

As a **user**,
I want **J.A.R.V.I.S. to gauge when to ask for confirmation**,
So that **routine tasks proceed smoothly while risky actions get approval**.

**Acceptance Criteria:**

**Given** an action has low risk (e.g., turning on lights)
**When** it's part of a plan
**Then** J.A.R.V.I.S. executes without asking
**And** logs the action for transparency

**Given** an action has high risk (e.g., unlocking doors, large purchases)
**When** it's part of a plan
**Then** J.A.R.V.I.S. requests explicit confirmation
**And** explains the action clearly before proceeding

**Given** the user has established patterns
**When** similar actions are requested
**Then** J.A.R.V.I.S. learns what needs confirmation vs. what can proceed
**And** calibrates over time based on feedback

---

### Story 7.5: Parallel Skill Coordination

As a **developer**,
I want **the orchestrator to run independent actions concurrently**,
So that **multi-step tasks complete faster**.

**Acceptance Criteria:**

**Given** a plan has independent steps (e.g., "dim lights" and "set thermostat")
**When** the orchestrator executes
**Then** both run in parallel using asyncio.gather
**And** the user sees combined feedback

**Given** a plan has dependent steps (e.g., "unlock door" then "disarm alarm")
**When** the orchestrator executes
**Then** steps run sequentially with proper ordering
**And** dependencies are respected

**Given** parallel steps include one failure
**When** others succeed
**Then** successful results are kept
**And** the failure is reported for resolution

---

## Epic 8: Distributed Presence

**Goal:** J.A.R.V.I.S. exists across multiple devices with seamless handoff and synchronized state. (Phase 3)

### Story 8.1: Client-Server Architecture

As a **developer**,
I want **J.A.R.V.I.S. split into a central server and lightweight clients**,
So that **multiple devices can connect to a single brain**.

**Acceptance Criteria:**

**Given** the server is running
**When** a client connects
**Then** authentication is performed via API key or token
**And** a WebSocket connection is established for real-time communication

**Given** multiple clients are connected
**When** commands are issued
**Then** they are routed to the central server for processing
**And** responses are returned to the originating client

**Given** the server handles multiple clients
**When** load increases
**Then** connections remain stable
**And** latency stays acceptable for voice interaction

---

### Story 8.2: Room-Aware Presence

As a **user**,
I want **J.A.R.V.I.S. to know which room I'm in**,
So that **he responds from the nearest device and uses location context**.

**Acceptance Criteria:**

**Given** clients are configured with room locations
**When** I speak to J.A.R.V.I.S.
**Then** the client in my room processes the wake word
**And** response is delivered from that room's speaker

**Given** presence is detected in a room
**When** J.A.R.V.I.S. makes proactive announcements
**Then** they are delivered to the room where I am
**And** other rooms remain silent (unless configured otherwise)

**Given** I move between rooms
**When** presence shifts
**Then** J.A.R.V.I.S. awareness follows
**And** context is maintained across the handoff

---

### Story 8.3: Conversation Handoff

As a **user**,
I want **to continue a conversation when I move to another room**,
So that **J.A.R.V.I.S. feels omnipresent rather than device-bound**.

**Acceptance Criteria:**

**Given** I'm in a conversation with J.A.R.V.I.S. in the living room
**When** I walk to the kitchen and continue speaking
**Then** J.A.R.V.I.S. seamlessly continues from the kitchen client
**And** conversation context is preserved

**Given** handoff occurs mid-sentence
**When** the new room picks up
**Then** J.A.R.V.I.S. acknowledges gracefully ("I'm with you, Sir")
**And** no context is lost

**Given** multiple rooms hear the same command
**When** determining which to respond from
**Then** the room with strongest signal/presence wins
**And** other rooms suppress their response

---

### Story 8.4: State Synchronization

As a **developer**,
I want **all clients to share synchronized state from the server**,
So that **memories, preferences, and context are consistent everywhere**.

**Acceptance Criteria:**

**Given** a preference is updated via any client
**When** the change is saved
**Then** all connected clients receive the update
**And** state is consistent across the system

**Given** a client reconnects after being offline
**When** it syncs with the server
**Then** it receives current state
**And** any queued local changes are reconciled

**Given** network partitions occur
**When** clients operate independently
**Then** they continue with cached state
**And** conflicts are resolved on reconnection (server wins)

---

### Story 8.5: Satellite Device Support

As a **user**,
I want **lightweight satellite devices (Raspberry Pi, smart speakers) to act as J.A.R.V.I.S. endpoints**,
So that **I can place him throughout my home affordably**.

**Acceptance Criteria:**

**Given** a satellite device is configured
**When** it boots
**Then** it connects to the central server
**And** handles local wake word detection and audio I/O

**Given** a command is detected on a satellite
**When** processing is needed
**Then** audio is streamed to the server for STT/LLM
**And** TTS audio is streamed back for playback

**Given** the server is unreachable
**When** a satellite is isolated
**Then** it provides limited offline functionality
**And** queues requests for when connection restores
