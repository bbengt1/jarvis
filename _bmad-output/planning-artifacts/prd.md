---
stepsCompleted: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
inputDocuments:
  - '_bmad-output/analysis/brainstorming-session-2026-01-03.md'
  - 'docs/index.md'
  - 'docs/architecture.md'
  - 'docs/project-context.md'
  - 'docs/api-reference.md'
  - 'docs/skills-guide.md'
  - 'docs/llm-providers.md'
  - 'docs/home-automation.md'
workflowType: 'prd'
lastStep: 0
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 1
  projectDocs: 7
---

# Product Requirements Document - J.A.R.V.I.S.

**Author:** Brent
**Date:** 2026-01-03

## Executive Summary

J.A.R.V.I.S. (Just A Rather Very Intelligent System) is evolving from a capable voice-activated assistant into a true Iron Man-style AI companion. The current system provides wake word detection, multi-provider LLM support, speech recognition, text-to-speech, computer vision, home automation, and an extensible skills framework - all running locally-first for privacy and low latency.

This PRD defines the transformation from reactive voice assistant to proactive AI partner through three architectural shifts:
1. **Reactive → Proactive**: Event bus, scheduler daemon, background processes for anticipatory behavior
2. **Forgetting → Remembering**: Persistent memory store for history, patterns, and relationship context
3. **Executing → Judging**: Multi-step planner with autonomous decision-making within trusted boundaries

The vision encompasses distributed presence (client/server architecture for multi-room and mobile access), full personality expression ("Sir", dry wit, sardonic but loyal), and spatial awareness via camera integration.

### What Makes This Special

The fundamental differentiator is **relationship, not features**. Existing voice assistants (Siri, Alexa, Google) possess similar capabilities but never feel like J.A.R.V.I.S. because they lack:

- **Continuity**: They forget; J.A.R.V.I.S. remembers years of context
- **Initiative**: They wait to be asked; J.A.R.V.I.S. observes, concludes, and volunteers
- **Judgment**: They ask permission for everything; J.A.R.V.I.S. makes decisions within boundaries
- **Relationship**: They are servants; J.A.R.V.I.S. is a partner with mutual respect

The moat isn't technology - it's accumulated shared history that becomes irreplaceable. Every interaction deepens the relationship, not just completes a task.

## Project Classification

**Technical Type:** IoT/Embedded + Desktop App Hybrid (distributed hardware presence with central Python backend)
**Domain:** AI/ML Systems + Home Automation
**Complexity:** High
**Project Context:** Brownfield - extending existing system with significant architectural evolution

This project builds upon a mature Python codebase with FastAPI, async-first patterns, and modular subsystem design. The evolution requires:
- New infrastructure (event bus, memory store, scheduler daemon)
- Architectural shift (single instance → client/server)
- Hardware prototyping (room nodes with mic/speaker/camera)
- Multi-phase delivery spanning foundation, proactive core, and full autonomy

## Success Criteria

### User Success

**The Relationship Test:** J.A.R.V.I.S. feels like a trusted partner, not a voice-activated tool. Success is measured by:

- **Proactive Value**: J.A.R.V.I.S. volunteers useful information without being asked at least once daily
- **Trust Threshold**: User delegates tasks with "figure it out" and trusts the outcome
- **Personality Authenticity**: The "Sir" + dry wit feels natural, not forced - consistent character across all interactions
- **Context Awareness**: J.A.R.V.I.S. references past conversations, preferences, and patterns accurately
- **Anticipation**: User receives relevant information before explicitly asking for it

**The Morning Briefing Test:** Wake up to a synthesized summary that actually saves time and surfaces what matters - not information overload.

**The Evening Transition Test:** Seamless mode shift with appropriate automation, day summary, and tomorrow preview.

### Business Success

As a personal project, business success = personal utility and satisfaction:

- **3 Months**: Foundation complete - persistent memory working, personality consistent, event bus responding to home events
- **6 Months**: Proactive core operational - morning briefings happening, scheduler daemon running, pattern recognition emerging
- **12 Months**: Full autonomy for routine tasks - "figure it out" orchestration working for common scenarios

**Daily Active Use Threshold:** J.A.R.V.I.S. provides genuine value every day, not just novelty interactions.

### Technical Success

- **Reliability**: 99% uptime for core voice interaction on primary node
- **Latency**: Voice response within 2 seconds of speech completion
- **Memory Persistence**: Zero data loss on preferences, history, and relationship context
- **Graceful Degradation**: If cloud LLM unavailable, fall back to local Ollama
- **Client/Server**: At minimum 2 room clients + mobile client functional by Phase 3

### Measurable Outcomes

| Metric | Target | Measurement |
|--------|--------|-------------|
| Proactive suggestions | ≥1/day | Count of unsolicited valuable information |
| "Figure it out" success rate | ≥80% | Tasks delegated vs. tasks completed correctly |
| Context recall accuracy | ≥90% | Relevant history referenced when appropriate |
| Response latency (voice) | <2s | Time from speech end to audio response start |
| System uptime | ≥99% | Core services availability |

## Product Scope

### MVP - Minimum Viable Product (Phase 1)

Foundation layer that enables everything else:

- **Persistent Memory Store**: Preferences, history, relationship context (L2-L3)
- **Personality System Prompt**: Consistent "Sir" + dry wit character (X2-X3)
- **Event Bus Skeleton**: React to home events (doorbell, sensors, etc.) (P2)
- **Single Instance**: Current architecture refined, not yet distributed

**MVP Success**: A J.A.R.V.I.S. that remembers, sounds right, and reacts to events.

### Growth Features (Post-MVP - Phase 2)

Proactive core capabilities:

- **Scheduler Daemon**: Morning briefing, evening transition, scheduled checks
- **Integration Skills**: Email triage, 3D print monitoring, CI/CD status
- **Pattern Recognition**: "You usually..." anticipation based on history
- **Priority Intelligence**: User-defined urgency rules + sensible defaults

**Phase 2 Success**: J.A.R.V.I.S. proactively helps without being asked.

### Vision (Future - Phase 3)

Full Iron Man experience:

- **Multi-step Planner**: "Figure it out" orchestration across systems
- **Autonomous Actions**: Act then inform within trusted boundaries
- **Client/Server Architecture**: Distributed presence across rooms + mobile
- **Eyes (Stretch)**: Visual awareness via ArgusAI camera integration
- **Full Relationship Model**: Deep contextual understanding accumulated over time

**Vision Success**: The movie J.A.R.V.I.S. experience, adapted to reality.

## User Journeys

### Journey 1: Brent - A Perfect Day with J.A.R.V.I.S.

Brent wakes up on a Tuesday morning to J.A.R.V.I.S.'s familiar voice: "Good morning, Sir. I have your briefing ready."

Without getting out of bed, he listens as J.A.R.V.I.S. delivers a synthesized overnight summary - not a robotic list, but a prioritized narrative: "Your overnight 3D print completed successfully - the replacement bracket looks good. I noticed an edge case in your API integration while reviewing your test logs - null handling on line 247 of the validation module. Your package from Amazon is scheduled for delivery between 2 and 4 PM, and I've already blocked your calendar. Weather today is 72 and clear, excellent for the evening you mentioned wanting to grill."

Brent smiles. J.A.R.V.I.S. remembered the grilling comment from three days ago. "Thanks, J.A.R.V.I.S. What about the Hendersons?"

"The Hendersons confirmed dinner for Saturday. Based on your last dinner party preferences, I've prepared a suggested menu emphasizing grillable proteins. Shall I place a grocery order, or would you prefer to review first?"

"Let me see it later. I'm getting up."

"Very good, Sir. I've started the coffee maker."

During his workday, J.A.R.V.I.S. operates in the background - present but not intrusive. When the doorbell rings, J.A.R.V.I.S. announces calmly: "Sir, there's a delivery at the front door. Your Amazon package has arrived early." Brent decides to grab it now.

Later, a message comes in from his wife. J.A.R.V.I.S. doesn't interrupt his focused coding session - this isn't marked as urgent. But when the garage door opens unexpectedly at 2 PM, J.A.R.V.I.S. immediately notes: "Sir, the garage door has opened. I don't show any expected arrivals."

"Check the camera."

"It appears to be a neighbor's cat that triggered the motion sensor. I've closed the garage door. Shall I adjust the sensitivity?"

"Yes, please."

"Done, Sir. I'll monitor for any recurrence."

As evening approaches, J.A.R.V.I.S. initiates the transition: "Sir, it's 5:30. Your wife is 15 minutes away based on her usual route. I've adjusted the thermostat for evening comfort, queued your dinner playlist, and turned off the office lights you left on. Anything else before I shift to home mode?"

"Just the usual. Thanks, J.A.R.V.I.S."

"Of course, Sir. Do try to actually relax this evening - you've logged 11 hours of screen time today, which is above your preferred maximum."

That evening, while grilling, Brent calls out: "J.A.R.V.I.S., I'm having 8 people over Saturday. Handle it."

J.A.R.V.I.S. doesn't ask 47 questions. Instead: "Understood, Sir. I've cross-referenced your calendar - Saturday is clear. Based on the Hendersons dinner and the guest count, I suggest expanding to a backyard dinner party format. Your last successful party for 8 used the string lights, outdoor speakers, and the rectangular table configuration. I'll adjust the grocery order to account for 8, prepare a weather-appropriate backup plan, and send you a summary for approval in the morning. Is there anything you specifically want included?"

"Just make sure we have enough of that IPA Mike likes."

"Already noted from December, Sir. I've added a case to the order."

### Journey 2: Brent - The Multi-Room Morning (Phase 3 Vision)

Brent starts his morning in the bedroom, where the room client detects he's awake from motion and ambient noise. J.A.R.V.I.S. greets from the nearby speaker, delivering the briefing.

As Brent walks to the bathroom, the conversation continues seamlessly - the bedroom client hands off to the hallway client, which hands off to the bathroom client. The context carries forward mid-sentence.

"...and regarding the server migration, your CI/CD pipeline completed successfully at 3 AM. All tests passed."

In the kitchen, Brent asks for more detail on one item while making coffee. J.A.R.V.I.S. responds from the kitchen speaker, never missing a beat. The mobile app shows the same conversation thread - if Brent leaves for work, he can continue in the car.

When he steps outside, his phone becomes the primary client. "Sir, I notice you're heading to the car. Should I send the briefing summary to your phone for the commute?"

"Yes, and switch to audio only while I'm driving."

"Of course, Sir. Resuming in navigation-safe mode."

### Journey 3: Brent - The Unexpected Problem

It's 2 AM. J.A.R.V.I.S. detects that the network-attached storage (NAS) has stopped responding. Based on Brent's priority rules, this qualifies as urgent - it's the RAID array with irreplaceable data.

J.A.R.V.I.S. doesn't panic. It first runs diagnostics: the NAS is powered on but the web interface is unresponsive. SSH times out. Temperature sensors show elevated readings in the enclosure.

Decision point: Wake Brent, or attempt recovery first?

Based on learned patterns - Brent prefers to be informed of hardware issues immediately but doesn't want to be woken for things J.A.R.V.I.S. can handle - the AI makes a judgment call. It triggers the smart plug to power-cycle the NAS, sets a 5-minute timer, and prepares a notification.

The NAS comes back online. Temperatures normalize. J.A.R.V.I.S. logs the incident with full diagnostics but doesn't wake Brent.

In the morning briefing: "Sir, your NAS experienced a thermal event at 2:14 AM and became unresponsive. I performed a power cycle recovery, and it came back online at 2:21 AM. All RAID arrays are healthy. I recommend we investigate the cooling in that enclosure - this is the second thermal event this month."

Brent trusts the judgment. "Order a USB fan for the NAS shelf."

"Done, Sir. Arriving Thursday."

### Journey 4: Household Member - Guest in the Home

Brent's mother-in-law is staying for the weekend. J.A.R.V.I.S. has a "guest mode" for recognized household visitors.

When she walks into the kitchen on Saturday morning, J.A.R.V.I.S. greets warmly but differently: "Good morning, Carol. The coffee maker is ready - would you like me to start it?"

No "Sir." A warmer, more approachable tone. J.A.R.V.I.S. knows she prefers direct helpfulness over personality. She can ask for the weather, control the TV, or request help with the thermostat - basic interactions without the full relationship context.

"J.A.R.V.I.S., what time is the dinner party?"

"The guests are expected at 6 PM. Brent mentioned grilling would start around 5:30. Is there anything I can help you prepare?"

"What's the menu?"

"Based on Brent's plan, we're serving grilled ribeyes, Caesar salad, roasted vegetables, and a key lime pie. The wine is already chilling."

She's impressed but comfortable - J.A.R.V.I.S. is helpful without being intrusive.

### Journey 5: Administrator/Developer - Extending J.A.R.V.I.S.

Brent wants to add a new skill: monitoring his home solar panel production. He opens the web configuration UI at localhost:8080.

The Skills page shows all active skills with their status. He clicks "Add New Skill" and J.A.R.V.I.S. assists through the web UI: "What type of integration are you adding, Sir? I see you have solar panels from Enphase - I can help you connect to their API."

Using the API credentials he provides, J.A.R.V.I.S. suggests a skill structure: poll production data every 15 minutes, store daily summaries in memory, alert if production drops unexpectedly.

"I'd also recommend integrating this with your morning briefing - I can include daily production and battery status. Shall I set that up?"

Brent confirms, and J.A.R.V.I.S. generates the skill file from a template, tests the API connection, and registers it with the skill framework. No manual code required for this common pattern.

Later, the morning briefing includes: "Your solar panels produced 42 kWh yesterday, 8% above the monthly average. Your Powerwall is at 94%."

### Journey Requirements Summary

These journeys reveal the following capability requirements:

| Journey | Key Capabilities Required |
|---------|--------------------------|
| Perfect Day | Morning briefing synthesis, event bus for home events, calendar integration, preference memory, orchestration ("figure it out"), personality system |
| Multi-Room | Client/server architecture, audio handoff, presence detection, mobile client, context continuity |
| Unexpected Problem | Autonomous decision-making, priority rules engine, hardware integration, incident logging, pattern recognition |
| Guest Interaction | User profiles/personas, guest mode, simplified interaction layer, privacy boundaries |
| Developer Extension | Web configuration UI, skill templates, API integration helpers, memory store, testing framework |

**Core Capabilities Across All Journeys:**
- Persistent memory store (preferences, patterns, history)
- Event bus (home automation, sensors, notifications)
- Priority intelligence (what warrants interruption)
- Personality system (tone, character, relationship)
- Multi-step planner (orchestration for complex requests)
- Client/server architecture (distributed presence)

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Relationship-First Architecture**

The fundamental innovation is designing around *relationship* rather than *capability*. Where existing voice assistants optimize for task completion, J.A.R.V.I.S. optimizes for relationship depth. This inverts the traditional priority stack:

| Traditional Voice Assistant | J.A.R.V.I.S. Innovation |
|----------------------------|------------------------|
| Feature set → User satisfaction | Relationship depth → Features emerge |
| Session-based memory | Persistent relationship memory |
| Reactive to commands | Proactive from understanding |
| Consistent neutral tone | Evolving personality expression |
| Permission for everything | Judgment within trusted boundaries |

**2. Proactive AI Companion Pattern**

Unlike any consumer voice assistant, J.A.R.V.I.S. implements true proactivity through:
- Event-driven observation and response
- Pattern recognition leading to anticipation
- Autonomous action within user-defined boundaries
- "Act then inform" rather than "ask then act"

**3. Distributed Presence with Unified Context**

The client/server architecture with seamless handoff is novel for personal AI:
- Single relationship spanning multiple physical locations
- Audio context that follows the user through spaces
- Presence detection determining which client is active
- Mobile extension of the same conversation

**4. "Figure It Out" Orchestration**

Multi-step autonomous planning that infers intent from vague requests:
- "I'm having 8 people over Saturday" → Full event planning
- No 47 questions - make decisions, confirm once
- Draws on historical context for preferences
- Coordinates across multiple systems (calendar, shopping, home automation)

### Market Context & Competitive Landscape

**Why This Hasn't Been Done:**
- **Siri/Alexa/Google**: Built for mass market → personality and relationship are risky at scale
- **Commercial assistants**: Privacy constraints prevent deep personalization
- **Local-first requirement**: Cloud-dependent assistants can't accumulate local relationship data the same way
- **Complexity**: True proactivity requires architectural decisions big companies won't make for 1% improvement

**Why J.A.R.V.I.S. Can:**
- Personal project → can take design risks
- Single user → deep personalization is the point
- Local-first → memory stays private
- Owner-developer → can iterate based on real daily use

### Validation Approach

**Phase 1 (Foundation) Validation:**
- Does memory feel continuous across days/weeks?
- Does personality feel consistent and authentic?
- Do events trigger appropriate responses?

**Phase 2 (Proactive) Validation:**
- Are proactive suggestions valuable or annoying?
- Does pattern recognition improve over time?
- Is the morning briefing worth listening to?

**Phase 3 (Autonomy) Validation:**
- Does "figure it out" produce acceptable results?
- Are autonomous decisions within acceptable boundaries?
- Does distributed presence feel seamless?

**The Ultimate Validation:** Would you trust J.A.R.V.I.S. with progressively more autonomy?

### Risk Mitigation

| Innovation Risk | Mitigation Strategy |
|----------------|---------------------|
| Memory becomes creepy | User controls what's remembered; transparency about what's stored |
| Proactivity is annoying | Start conservative; user-tunable sensitivity; easy "stop that" |
| Personality feels forced | Iterate on system prompt based on real interactions |
| Autonomy makes mistakes | Undo/rollback for actions; incident logging; escalation rules |
| Distributed presence fails | Graceful degradation to single-room mode |
| "Figure it out" fails | Confirm complex plans before execution; learn from corrections |

**Fallback Philosophy:** Each innovation layer should degrade gracefully to the layer below. If autonomy fails, fall back to proactive. If proactive fails, fall back to reactive. The core voice assistant always works.

## IoT/Desktop Hybrid Technical Requirements

### Project-Type Overview

J.A.R.V.I.S. is a hybrid IoT/Desktop system consisting of:
- **Central Server**: Python backend running on dedicated hardware (Mac Mini, Raspberry Pi, or home server)
- **Room Clients**: Distributed audio/presence nodes throughout the house
- **Mobile Client**: Smartphone app for on-the-go access
- **Existing Components**: Wake word detection, multi-provider LLM, speech synthesis, home automation integration

This architecture enables the "distributed presence with unified context" innovation pattern.

### Hardware Requirements

#### Central Server (Brain)
| Component | Requirement | Rationale |
|-----------|-------------|-----------|
| CPU | Multi-core (4+) | Concurrent audio processing, LLM inference (if local) |
| RAM | 16GB+ recommended | Local LLM models, memory store, concurrent connections |
| Storage | SSD, 256GB+ | Fast access to memory store, audio processing |
| Network | Gigabit Ethernet preferred | Low-latency communication with clients |
| GPU | Optional (for local Ollama) | Accelerates local LLM inference |

#### Room Clients (Presence Nodes)
| Component | Requirement | Rationale |
|-----------|-------------|-----------|
| Hardware Base | Raspberry Pi 4/5 or equivalent | Cost-effective, Linux support |
| Microphone | USB mic array or ReSpeaker | Wake word detection, voice capture |
| Speaker | USB or 3.5mm audio out | TTS playback |
| Camera (Stretch) | USB webcam or Pi Camera | Visual awareness, presence detection |
| Network | WiFi 5+ or Ethernet | Audio streaming to server |

#### Mobile Client
| Platform | Requirement |
|----------|-------------|
| iOS | 15.0+ (native or React Native) |
| Android | API 26+ (Android 8.0+) |
| Features | Wake word, push notifications, context sync |

### Connectivity Protocol

#### Client-Server Communication
- Room Client ↔ Server: WebSocket (real-time audio, commands)
- Mobile Client ↔ Server: WebSocket + REST API
- Server ↔ Home Assistant: REST API + WebSocket
- Server ↔ MQTT Broker: MQTT (event bus)

**Protocol Choices:**
- **WebSocket**: Bidirectional real-time for audio streaming and instant responses
- **REST API**: Configuration, skill management, non-realtime operations
- **MQTT**: Event bus for home automation events, inter-service messaging
- **gRPC**: Optional for internal microservice communication (future)

#### Network Requirements
- Local network only (no cloud dependency for core functions)
- mDNS/Bonjour for client discovery
- TLS for all communications (even local)
- Fallback to direct IP if discovery fails

### Security Model

#### Authentication & Authorization
| Layer | Mechanism |
|-------|-----------|
| Server Access | API key + optional TLS client certs |
| Room Clients | Pre-shared key, enrolled during setup |
| Mobile Client | User authentication (PIN/biometric) + device token |
| Web UI | Session-based auth, HTTPS only |
| Guest Mode | Limited permission scope, no memory access |

#### Data Protection
- **Memory Store**: Encrypted at rest (AES-256)
- **Audio Streams**: TLS in transit, not persisted unless explicitly requested
- **API Keys**: Stored in system keychain, not plaintext config
- **Backups**: Encrypted, user-controlled export

#### Privacy Boundaries
- All processing local by default
- Cloud LLM opt-in with clear disclosure
- Guest interactions not stored in relationship memory
- Memory inspection/deletion via web UI

### Update Mechanism

#### Server Updates
- Git-based: `git pull && uv sync && systemctl restart jarvis`
- Version checking via GitHub releases API
- Rollback capability via git
- Database migrations for memory store schema changes

#### Client Updates
- Room clients: SSH-based push updates from server
- Mobile clients: App store distribution
- Configuration sync: Automatic on reconnect

### Platform Support

#### Server
| Platform | Support Level |
|----------|---------------|
| macOS (Apple Silicon) | Primary development platform |
| Linux (x86_64) | Fully supported |
| Linux (ARM64) | Fully supported (Raspberry Pi) |
| Windows | Best effort (WSL2 recommended) |

#### Room Clients
| Platform | Support Level |
|----------|---------------|
| Raspberry Pi OS | Primary target |
| Ubuntu/Debian ARM | Supported |
| Other Linux | Community contributions |

### System Integration

#### Existing Integrations (Maintained)
- **Home Assistant**: Full REST API + WebSocket for real-time state
- **MQTT**: Event bus for sensors, automation triggers
- **Ollama**: Local LLM inference
- **Cloud LLMs**: OpenAI, Anthropic, Google, xAI (optional)

#### New Integrations (Phased)
| Phase | Integration | Purpose |
|-------|-------------|---------|
| 1 | SQLite/PostgreSQL | Persistent memory store |
| 2 | Email (IMAP) | Email triage skill |
| 2 | Calendar (CalDAV) | Calendar awareness beyond local |
| 2 | OctoPrint/Bambu | 3D print monitoring |
| 3 | ArgusAI | Visual awareness (existing) |
| 3 | Grocery APIs | Automated ordering |

### Offline Capabilities

#### Core Offline Functions
- Wake word detection (OpenWakeWord runs locally)
- Speech recognition (Whisper runs locally)
- TTS synthesis (Piper runs locally)
- Home automation commands (if HA accessible)
- Memory access and pattern matching
- Skill execution for local-only skills

#### Degraded Mode (No Internet)
- Cloud LLM unavailable → Fallback to Ollama
- External APIs (weather, etc.) → Cached last-known + notification
- Push notifications → Queued for delivery when online

#### Degraded Mode (Server Unreachable)
- Room clients → Announce "I'm having trouble connecting to the server"
- Mobile client → Cached recent context, limited functionality
- No command execution until server reconnects

### Implementation Considerations

#### Phase 1 Focus
- Single-instance architecture (no clients yet)
- Memory store with SQLite backend
- Personality system prompt refinement
- Event bus skeleton with MQTT

#### Phase 2 Focus
- Scheduler daemon for proactive behaviors
- Pattern recognition engine
- Additional integration skills

#### Phase 3 Focus
- Client/server split
- Room client prototype (Raspberry Pi + mic + speaker)
- Audio streaming protocol implementation
- Presence detection and handoff logic
- Mobile client development

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Platform MVP - Build the relationship substrate

Unlike traditional MVPs focused on user acquisition or revenue, J.A.R.V.I.S. MVP success is measured by:
- Does it remember things that matter?
- Does it sound like J.A.R.V.I.S.?
- Does it notice things happening in the house?

These three capabilities are the foundation for everything that follows. Without persistent memory, there's no relationship. Without personality, there's no J.A.R.V.I.S. Without event awareness, there's no proactivity.

**Resource Requirements:**
- Solo developer (owner-operator model)
- Existing codebase provides strong foundation
- No external dependencies beyond existing integrations
- Primary time investment: evenings and weekends

### MVP Feature Set (Phase 1)

**Core User Journey Supported:** Journey 1 (Perfect Day) - Foundation elements only

**Must-Have Capabilities:**

| Capability | Rationale | Implementation |
|------------|-----------|----------------|
| Persistent Memory Store | Substrate of relationship - without this, no continuity | SQLite-backed storage for preferences, history, patterns |
| Personality System Prompt | Immediate impact on every interaction - the "Sir" and dry wit | Refined system prompt with consistent character |
| Event Bus Skeleton | Foundation for proactivity - react to home events | MQTT integration for HA events |
| Preference Learning | Start building the relationship - remember what matters | Explicit + implicit preference capture |

**Explicitly Deferred:**
- Scheduler daemon (Phase 2)
- Morning/evening briefings (Phase 2)
- Pattern recognition (Phase 2)
- Multi-step planner (Phase 3)
- Autonomous actions (Phase 3)
- Room clients (Phase 3)
- Mobile client (Phase 3)
- Camera integration (Phase 3 stretch)

**MVP Success Criteria:**
1. Ask J.A.R.V.I.S. about something from last week → accurate recall
2. Every response sounds like J.A.R.V.I.S. (consistent personality)
3. Doorbell rings → J.A.R.V.I.S. announces it without being asked

### Post-MVP Features

**Phase 2: Proactive Core**

| Feature | User Value | Dependencies |
|---------|------------|--------------|
| Scheduler Daemon | Morning briefing, evening transition | Memory store, event bus |
| Pattern Recognition | "You usually..." anticipation | Memory store with history |
| Priority Intelligence | Interrupt appropriately | Event bus, preference memory |
| Integration Skills | Email, 3D print, CI/CD awareness | Event bus, memory store |

**Phase 2 Success Criteria:**
1. Wake up to a useful morning briefing
2. J.A.R.V.I.S. anticipates at least one thing correctly per week
3. Urgent things interrupt; non-urgent things wait

**Phase 3: Full Autonomy**

| Feature | User Value | Dependencies |
|---------|------------|--------------|
| Multi-step Planner | "Figure it out" orchestration | Pattern recognition, memory |
| Autonomous Actions | Act then inform | Priority intelligence, trust model |
| Client/Server Split | Distributed presence | Core architecture change |
| Room Clients | J.A.R.V.I.S. throughout the house | Client/server architecture |
| Mobile Client | On-the-go access | Client/server architecture |
| Visual Awareness (Stretch) | Spatial context | ArgusAI integration |

**Phase 3 Success Criteria:**
1. "I'm having 8 people over Saturday" produces a reasonable plan
2. J.A.R.V.I.S. makes a good autonomous decision
3. Walk between rooms without losing conversation

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Memory store schema changes break history | Medium | High | Version schema from day 1; migration scripts |
| Personality feels artificial | Medium | Medium | Iterate on system prompt based on real use; A/B test variations |
| Event bus misses important events | Low | Medium | Comprehensive HA event logging; monitor for gaps |
| Local LLM performance insufficient | Low | Low | Ollama already working; cloud fallback exists |

**Scope Risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Phase 2 takes longer than expected | High | Medium | Clear phase boundaries; celebrate Phase 1 wins |
| Hardware prototyping blocks Phase 3 | Medium | Medium | Can prototype with existing hardware (Mac Mini as first "client") |
| Scope creep in Phase 1 | Medium | High | Strict MVP definition; defer everything not in table above |

**Relationship Risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Memory becomes overwhelming | Low | Medium | Relevance scoring; forgetting mechanism for unimportant things |
| Personality becomes annoying | Medium | Medium | Easy "less personality" setting; context-aware tone |
| Proactivity becomes intrusive | Medium | Medium | Conservative defaults; user-tunable sensitivity |

### Development Sequence

```
Current State
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Foundation (MVP)                               │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │   Memory    │ │ Personality │ │  Event Bus  │        │
│ │   Store     │ │   System    │ │  Skeleton   │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                         │
│ Success: Remembers + Sounds right + Reacts to events   │
└─────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Proactive Core                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │  Scheduler  │ │   Pattern   │ │  Priority   │        │
│ │   Daemon    │ │ Recognition │ │Intelligence │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                         │
│ Success: Proactively helps without being asked          │
└─────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: Full Autonomy                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │  Multi-step │ │   Client/   │ │   Visual    │        │
│ │   Planner   │ │   Server    │ │  Awareness  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                         │
│ Success: The movie J.A.R.V.I.S. experience              │
└─────────────────────────────────────────────────────────┘
```

### Scope Boundaries

**In Scope (All Phases):**
- Personal use only (single user + household guests)
- Local-first architecture (cloud optional)
- English language only
- Home environment focus

**Out of Scope (Never):**
- Multi-user/commercial deployment
- Cloud-required functionality
- Other languages (may reconsider later)
- Work/office environment optimization

## Functional Requirements

### Memory & Context

- FR1: System can persist user preferences, history, and relationship context across sessions
- FR2: System can recall relevant context from previous conversations when appropriate
- FR3: System can learn implicit preferences from user behavior patterns
- FR4: System can store explicit preferences when user states them
- FR5: User can view what J.A.R.V.I.S. remembers about them
- FR6: User can delete specific memories or preference data
- FR7: System can associate memories with temporal context (when things happened)
- FR8: System can prioritize recent and frequently-referenced memories over old, rarely-used ones

### Personality & Character

- FR9: System can respond with consistent personality across all interactions ("Sir", dry wit, formal but trusted peer)
- FR10: System can adapt tone based on context (e.g., more direct for urgent matters)
- FR11: System can make observations and offer unsolicited but relevant comments
- FR12: System can express opinions within appropriate boundaries
- FR13: System can maintain character consistency across different interaction modes (voice, text, web UI)

### Event Awareness & Proactivity

- FR14: System can receive and process events from home automation systems
- FR15: System can announce relevant events to the user without being asked
- FR16: System can filter events based on user-defined priority rules
- FR17: System can determine appropriate timing for event announcements
- FR18: System can correlate multiple events into meaningful summaries
- FR19: System can detect patterns in events and learn from them (Phase 2)
- FR20: System can initiate conversations based on scheduled triggers (Phase 2)
- FR21: System can deliver synthesized morning briefings (Phase 2)
- FR22: System can manage evening transition with day summary (Phase 2)

### Voice Interaction

- FR23: System can detect wake word and activate listening
- FR24: System can transcribe spoken commands using speech recognition
- FR25: System can respond with synthesized speech
- FR26: User can interrupt J.A.R.V.I.S. during speech playback
- FR27: System can handle multi-turn conversations with context
- FR28: System can operate in hands-free mode continuously

### Home Automation Integration

- FR29: System can control smart home devices (lights, locks, climate, media, covers)
- FR30: System can query device states and report to user
- FR31: System can execute scenes and automations by name
- FR32: System can suggest appropriate automations based on context
- FR33: System can coordinate multiple device actions atomically
- FR34: System can receive real-time state updates from home automation

### Orchestration & Planning

- FR35: System can break down high-level requests into multiple actions (Phase 3)
- FR36: System can create plans that span multiple systems (calendar, home, shopping) (Phase 3)
- FR37: System can present plans for user approval before execution (Phase 3)
- FR38: System can execute approved plans autonomously (Phase 3)
- FR39: System can learn from plan corrections and improve future suggestions (Phase 3)
- FR40: System can act autonomously within user-defined boundaries (Phase 3)
- FR41: System can inform user of autonomous actions taken (Phase 3)

### User & Guest Management

- FR42: System can recognize the primary user
- FR43: System can interact with household guests in simplified mode
- FR44: Guest interactions are not stored in relationship memory
- FR45: System can adapt personality for different recognized individuals
- FR46: System can limit guest access to appropriate functionality

### Skills & Integration

- FR47: User can invoke built-in skills (weather, calendar, reminders, time)
- FR48: System can provide weather information for configured location
- FR49: System can manage calendar events (view, create, modify)
- FR50: System can set and manage reminders with notifications
- FR51: System can query ArgusAI camera system for security events
- FR52: System can integrate with email for triage and summaries (Phase 2)
- FR53: System can monitor 3D print status (Phase 2)
- FR54: System can check CI/CD pipeline status (Phase 2)

### Distributed Presence (Phase 3)

- FR55: System can receive input from multiple room clients
- FR56: System can route audio output to appropriate room client
- FR57: System can maintain conversation context across room transitions
- FR58: System can detect user presence in rooms
- FR59: System can hand off active conversation between clients seamlessly
- FR60: Mobile client can connect to system remotely

### Configuration & Administration

- FR61: User can configure system settings via web interface
- FR62: User can switch between LLM providers at runtime
- FR63: User can manage API keys and credentials securely
- FR64: User can configure skill-specific settings
- FR65: User can define priority rules for event interruptions
- FR66: User can add new skills without modifying core code
- FR67: User can view system logs and diagnostic information
- FR68: User can backup and restore system configuration and memory

### Requirements Summary by Phase

**Phase 1 (MVP):** FR1-FR8, FR9-FR13, FR14-FR18, FR23-FR28, FR29-FR34, FR42-FR46, FR47-FR51, FR61-FR68

**Phase 2:** FR19-FR22, FR52-FR54

**Phase 3:** FR35-FR41, FR55-FR60

## Non-Functional Requirements

### Performance

**NFR1: Voice Response Latency**
- System must begin audio response within 2 seconds of speech completion
- Wake word detection must respond within 500ms
- TTS playback must begin within 1 second of text generation
- Target: 95th percentile under 2.5 seconds end-to-end

**NFR2: Memory Store Performance**
- Preference retrieval must complete within 100ms
- Context search across history must complete within 500ms
- Memory write operations must not block voice interaction

**NFR3: Event Processing Latency**
- Home automation events must be processed within 1 second of receipt
- Event-triggered announcements must begin within 2 seconds
- Event correlation (multiple related events) must complete within 3 seconds

**NFR4: Concurrent Operations**
- System must handle simultaneous audio input, LLM generation, and TTS output
- Event processing must not block voice interaction
- Background tasks (scheduler, pattern recognition) must not impact foreground responsiveness

### Security

**NFR5: Data Protection**
- Memory store must be encrypted at rest using AES-256 or equivalent
- All API keys and credentials must be stored in system keychain, not plaintext
- Audio streams must not be persisted unless explicitly configured

**NFR6: Communication Security**
- All client-server communication must use TLS 1.3 or higher
- All web UI access must use HTTPS
- Room clients must authenticate with pre-shared keys

**NFR7: Privacy Boundaries**
- Guest interactions must not be stored in relationship memory
- Cloud LLM usage must be opt-in with clear disclosure
- User must be able to view and delete any stored data

**NFR8: Access Control**
- Web UI must require authentication
- Mobile client must support biometric or PIN authentication
- Guest mode must limit access to predefined functionality only

### Reliability

**NFR9: System Availability**
- Core voice interaction must achieve 99% uptime (measured monthly)
- Scheduled downtime for updates must be announced in advance
- System must recover automatically from transient failures

**NFR10: Graceful Degradation**
- If cloud LLM unavailable, system must fall back to local Ollama
- If internet unavailable, local functionality must continue
- If memory store unavailable, system must operate in stateless mode with warning

**NFR11: Data Durability**
- Memory store must survive unexpected shutdown without data loss
- Configuration changes must be persisted immediately
- Critical data must be backed up daily (configurable)

**NFR12: Error Recovery**
- Failed voice recognition must not crash the system
- LLM timeouts must be handled gracefully with retry
- Home automation failures must be logged and announced appropriately

### Integration

**NFR13: Home Assistant Compatibility**
- Must support Home Assistant 2024.1+ REST API
- Must maintain persistent WebSocket connection for real-time state
- Must handle Home Assistant restarts gracefully

**NFR14: LLM Provider Compatibility**
- Must support Ollama for local inference
- Must support OpenAI, Anthropic, Google, and xAI APIs
- Provider switching must complete within 5 seconds

**NFR15: MQTT Integration**
- Must support MQTT 3.1.1 and 5.0 protocols
- Must handle broker disconnection and automatic reconnection
- Must support QoS levels 0, 1, and 2

**NFR16: Extensibility**
- New skills must be addable without core code changes
- Skill interface must remain stable across minor versions
- Configuration schema must support skill-specific settings

### Usability

**NFR17: Voice Interaction Quality**
- Wake word must have less than 5% false positive rate in quiet environments
- Speech recognition must achieve 95% accuracy for clear speech
- TTS output must be clearly intelligible at normal conversation volume

**NFR18: Configuration Accessibility**
- All settings must be configurable via web UI
- Critical settings must also be configurable via voice
- Configuration changes must take effect without system restart (where possible)

**NFR19: Error Communication**
- Errors must be communicated in natural language, not technical jargon
- System must suggest remediation when possible
- Critical errors must be announced via TTS if voice is operational

### Maintainability

**NFR20: Logging**
- All significant events must be logged with timestamps
- Log levels must be configurable (DEBUG, INFO, WARNING, ERROR)
- Logs must be rotated to prevent disk exhaustion

**NFR21: Diagnostics**
- System health status must be viewable via web UI
- Integration connection status must be visible
- Memory store statistics must be available

**NFR22: Updateability**
- System must support rolling updates without data loss
- Database migrations must be automatic and reversible
- Configuration format changes must be backward compatible

### NFR Summary by Category

| Category | Count | Key Metrics |
|----------|-------|-------------|
| Performance | 4 | <2s voice latency, <100ms memory access |
| Security | 4 | AES-256 encryption, TLS 1.3, biometric auth |
| Reliability | 4 | 99% uptime, graceful degradation |
| Integration | 4 | HA 2024.1+, MQTT 5.0, multi-provider LLM |
| Usability | 3 | <5% false wake, 95% speech accuracy |
| Maintainability | 3 | Structured logging, health dashboard |

