<!-- GSD:project-start source:PROJECT.md -->
## Project

**BotCarnetConducir**

Bot de Telegram para practicar el examen teórico del permiso B en España. Permite responder preguntas de forma infinita, hacer exámenes tipo DGT con criterio de suspenso por más de tres fallos, consultar el banco de preguntas, proponer nuevas preguntas y ver estadísticas personales de aciertos y errores.

El producto está orientado a estudiantes que preparan el carnet B y quieren practicar desde Telegram sin depender de una app web o de Anki.

**Core Value:** Practicar preguntas reales o equivalentes del carnet B desde Telegram de forma rápida, continua y con feedback útil sobre errores.

### Constraints

- **Platform**: Solo Telegram bot — el usuario descartó panel web en v1.
- **Domain**: Permiso B, España — el producto debe hablar el lenguaje y reglas del examen español.
- **Content Source**: Importación inicial desde `anki-carnet-conducir` — reduce coste inicial y acelera MVP.
- **Licensing**: Dependencia de contenido con GPL-3.0 — obliga a revisar distribución y atribución antes de publicar.
- **Media Pipeline**: Imágenes asociadas no están completas en el repo principal — el importador debe tolerar preguntas sin imagen y gestionar medios por separado.
- **Quality**: Preguntas añadidas por usuarios no deben degradar el examen principal — deben persistirse con metadatos de origen y estado.
- **UX**: Flujo conversacional corto y claro — Telegram penaliza interfaces largas o ambiguas.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

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
# Core
# Supporting
# Dev dependencies
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
- Use SQLite with WAL mode
- Because it keeps ops minimal and suits low-to-medium traffic
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
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
