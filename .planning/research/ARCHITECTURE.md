# Architecture Research

**Domain:** Telegram study bot for Spanish driving theory exam preparation
**Researched:** 2026-05-25
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Interaction                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ /start/menu  │  │ callbacks    │  │ media responses  │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                   │             │
├─────────┴─────────────────┴───────────────────┴─────────────┤
│                       Bot Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ handlers     │  │ exam engine  │  │ practice engine  │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                   │             │
│  ┌──────┴─────────────────┴───────────────────┴──────────┐  │
│  │ submission service / stats service / question service │  │
│  └──────────────────────────────┬────────────────────────┘  │
├─────────────────────────────────┴───────────────────────────┤
│                         Persistence                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ questions DB │  │ sessions DB  │  │ answer events DB │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Telegram handlers | Parse commands, callbacks, and free-text submissions | `python-telegram-bot` conversation handlers and callback query handlers |
| Question service | Retrieve canonical questions and options | Repository/service layer over DB |
| Practice engine | Select next practice question and evaluate answer | Pure application service |
| Exam engine | Start exam, track mistakes, compute pass/fail | Stateful application service with persistence |
| Submission service | Validate and persist user-created questions | Validation models plus DB tables |
| Stats service | Aggregate answer history into user-facing metrics | SQL queries or lightweight reporting layer |
| Import pipeline | Normalize upstream JSON and asset references | Offline script/CLI command |

## Recommended Project Structure

```text
src/
├── bot/                  # Telegram entrypoints and handlers
│   ├── commands/         # /start, /menu, admin-like commands
│   ├── callbacks/        # inline keyboard actions
│   └── conversations/    # multi-step submission and exam flows
├── domain/               # business rules
│   ├── exams/            # exam scoring and lifecycle
│   ├── practice/         # question selection rules
│   ├── questions/        # canonical question models
│   └── stats/            # metrics aggregation logic
├── infra/                # DB, repositories, settings, logging
│   ├── db/
│   ├── repositories/
│   └── config/
├── importers/            # upstream dataset ingestion
└── tests/                # importer, domain, and bot flow tests
```

### Structure Rationale

- **`bot/`**: keeps Telegram-specific code away from domain rules.
- **`domain/`**: protects exam logic from framework churn.
- **`infra/`**: isolates persistence and configuration details.
- **`importers/`**: treats upstream content ingestion as a first-class concern.

## Architectural Patterns

### Pattern 1: Canonical Question Model

**What:** Normalize upstream and user-submitted questions into one internal shape.
**When to use:** Immediately, before building practice or exam flows.
**Trade-offs:** Small upfront effort, major downstream simplicity.

### Pattern 2: Persistent Conversation State

**What:** Persist exam and submission state outside process memory.
**When to use:** Any multi-step Telegram flow.
**Trade-offs:** More schema work, much better reliability across restarts.

### Pattern 3: Import-then-Serve

**What:** Import remote datasets into a local DB and serve only from local canonical data.
**When to use:** When upstream content is editable, versioned, or legally sensitive.
**Trade-offs:** Requires importer maintenance, avoids runtime coupling to upstream format.

## Data Flow

### Request Flow

```text
[Telegram user action]
    ↓
[Handler] → [Use case service] → [Repository] → [SQLite DB]
    ↓              ↓                  ↓              ↓
[Bot reply] ← [Result model] ← [Domain rule] ← [Stored data]
```

### State Management

```text
[Conversation state row]
    ↓
[Handler lookup] ←→ [Exam/submission actions] → [DB update]
```

### Key Data Flows

1. **Question import:** upstream JSON and image references → importer → canonical question rows.
2. **Practice answer:** question served → user answer callback → evaluation → answer event and stats update.
3. **Exam session:** exam starts → ordered question set persisted → answer sequence logged → final pass/fail summary returned.
4. **User submission:** multi-step capture → validation → pending question row with provenance metadata.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Single bot process plus SQLite is fine |
| 1k-20k users | Move to PostgreSQL, add better caching for question retrieval |
| 20k+ users | Separate workers for imports/analytics and tighten observability |

### Scaling Priorities

1. **First bottleneck:** answer-event writes and stats queries — fix with indexed tables and precomputed counters.
2. **Second bottleneck:** concurrent state updates in exams — fix with stronger transactional persistence.

## Anti-Patterns

### Anti-Pattern 1: Bot Logic Mixed With SQL Everywhere

**What people do:** handlers compose messages, scoring, and SQL inline.
**Why it's wrong:** impossible to test and fragile to change.
**Do this instead:** isolate domain services and repositories.

### Anti-Pattern 2: Treating User Submissions as Canonical Immediately

**What people do:** append directly into the same live pool.
**Why it's wrong:** low-quality questions corrupt trust and stats.
**Do this instead:** persist with status and source fields.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Telegram Bot API | Long polling or webhook through bot framework | Start with long polling for simpler MVP ops |
| Upstream dataset repo | Import script using downloaded or fetched source files | Runtime should not depend on upstream availability |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| bot ↔ domain | direct service calls | Keep Telegram objects out of domain layer |
| domain ↔ infra | repository interfaces | Eases DB migration later |

## Sources

- https://docs.python-telegram-bot.org/en/v21.0/index.html
- https://core.telegram.org/bots/api
- https://github.com/donmerendolo/anki-carnet-conducir

---
*Architecture research for: Telegram study bot for Spanish driving theory exam preparation*
*Researched: 2026-05-25*
