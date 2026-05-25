# Stack Research

**Domain:** Telegram study bot for Spanish driving theory exam preparation
**Researched:** 2026-05-25
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12 | Main application runtime | Strong ecosystem for Telegram bots, data import scripts, and rapid backend iteration |
| python-telegram-bot | 21.x | Telegram Bot API integration | Officially maintained, async-first, includes conversation handling, persistence hooks, jobs, and media sending patterns |
| SQLite | 3.x | Primary persistence for MVP | Sufficient for a single bot deployment, trivial local setup, good fit for question bank, sessions, and statistics |
| SQLAlchemy | 2.x | Data access layer | Keeps schema, migrations, and query logic structured without locking the project into raw SQL everywhere |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Alembic | 1.x | Database migrations | Use from the first persisted schema to avoid ad hoc DB drift |
| Pydantic | 2.x | Data validation for imported questions and bot payloads | Use for parsing upstream JSON and validating user-submitted questions |
| httpx | 0.27.x | External HTTP requests | Use if importing upstream files programmatically or fetching remote assets |
| pytest | 8.x | Automated testing | Use for importer, scoring rules, and conversation state logic |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| ruff | Linting and formatting | Fast Python lint/format baseline |
| mypy | Static typing | Valuable in stateful bot flows and scoring logic |
| uv | Dependency management | Fast install and lock workflow for Python projects |

## Installation

```bash
# Core
uv add python-telegram-bot sqlalchemy pydantic

# Supporting
uv add alembic httpx

# Dev dependencies
uv add --dev pytest ruff mypy
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| python-telegram-bot | aiogram | If the team already prefers aiogram and wants more explicit FSM patterns |
| SQLite | PostgreSQL | When multiple bot instances, heavier analytics, or admin tooling arrive |
| SQLAlchemy | raw sqlite3 | Only for throwaway prototypes with almost no relational logic |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| In-memory only session state | Bot restarts lose exams, practice progress, and user stats | Persistent DB-backed session storage |
| Directly querying upstream JSON on every command | Slow, brittle, and blocks local editorial control | One-time importer plus local canonical question bank |
| Premature microservices | Adds deployment and debugging cost for a small MVP | Single deployable bot service with clear modules |

## Stack Patterns by Variant

**If deployment remains single-instance:**
- Use SQLite with WAL mode
- Because it keeps ops minimal and suits low-to-medium traffic

**If moderation/admin grows later:**
- Promote DB to PostgreSQL and expose a thin internal admin API
- Because review workflows and analytics queries will get heavier

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `python-telegram-bot@21.x` | `Python 3.8+` | Official docs indicate async interface and persistence support in the v21 line |
| `SQLAlchemy@2.x` | `Alembic@1.x` | Standard pairing for typed ORM plus migrations |

## Sources

- https://docs.python-telegram-bot.org/en/v21.0/index.html — verified async interface, persistence-related modules, supported Bot API line
- https://core.telegram.org/bots/api — verified Bot API capabilities such as media sending and inline keyboards
- https://github.com/donmerendolo/anki-carnet-conducir — verified source dataset shape, repo structure, and licensing context

---
*Stack research for: Telegram study bot for Spanish driving theory exam preparation*
*Researched: 2026-05-25*
