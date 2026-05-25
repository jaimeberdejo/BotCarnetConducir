# Feature Research

**Domain:** Telegram study bot for Spanish driving theory exam preparation
**Researched:** 2026-05-25
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Practice mode with immediate correction | Core study loop for theory-test products | LOW | Must show right/wrong answer and brief explanation |
| Exam mode with final score | Users want realistic simulation before sitting the test | MEDIUM | Needs configurable exam size and fail threshold logic |
| Image support in questions | Driving theory content often depends on signs and road situations | MEDIUM | Must gracefully handle missing images |
| Progress tracking | Users expect to know if they are improving | MEDIUM | Per-user stats are enough for MVP |
| Question bank import and normalization | Without content there is no product | MEDIUM | Importer must map upstream JSON into canonical schema |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Infinite practice with adaptive repetition later | Makes Telegram viable as a daily study tool | MEDIUM | Start simple, keep data model ready for spaced repetition |
| User-submitted questions | Keeps content growing and localizable | MEDIUM | Needs review status and provenance |
| Error-focused statistics | Helps users focus weak areas instead of random drilling | MEDIUM | Can evolve into tag/topic-based remediation |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Public crowd-editing of live exam bank | Feels collaborative and fast | Destroys trust if bad questions enter the main pool | Separate submissions from canonical imported bank |
| Full web admin in MVP | Seems useful for management | Expands scope into a second product surface | Use DB-backed states and optional admin commands later |
| AI-generated replacement questions at launch | Promises infinite content | High hallucination and legal/pedagogical risk | Start from imported curated bank plus human submissions |

## Feature Dependencies

```text
Question import
    └──requires──> canonical question schema
                           └──requires──> persistence layer

Practice mode
    └──requires──> question retrieval
                           └──requires──> canonical question schema

Exam mode
    └──requires──> practice-grade answer evaluation
                           └──requires──> persistence layer

User statistics
    └──requires──> answer event logging

User submissions
    └──requires──> question schema
    └──requires──> provenance and status metadata
```

### Dependency Notes

- **Practice mode requires canonical question retrieval:** otherwise every upstream format quirk leaks into the bot flow.
- **Exam mode requires answer evaluation and persistence:** the bot must track current exam, mistakes, and final result consistently.
- **Statistics require answer event logging:** summary-only counters are too limiting for future analytics.
- **User submissions require provenance metadata:** imported and user-created questions must remain distinguishable.

## MVP Definition

### Launch With (v1)

- [ ] Import local editable bank for permiso B — essential content foundation
- [ ] Practice mode with immediate correction — essential daily study loop
- [ ] Exam mode with fail-on-more-than-three-errors rule — essential realism
- [ ] Browse question bank by question detail — essential transparency and trust
- [ ] User question submission flow — explicitly requested scope
- [ ] Per-user stats of correct and incorrect answers — explicitly requested scope

### Add After Validation (v1.x)

- [ ] Review queue for submitted questions inside admin-only bot commands — add when submissions become frequent
- [ ] Topic/tag-based weak-area practice — add when enough answer history exists

### Future Consideration (v2+)

- [ ] Spaced repetition or adaptive drill mode — defer until baseline retention data exists
- [ ] Multi-permit support (A1, D) — defer until carnet B workflow is proven
- [ ] Web dashboard — defer because current scope is Telegram-only

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Practice mode | HIGH | MEDIUM | P1 |
| Exam mode | HIGH | MEDIUM | P1 |
| Importer and media mapping | HIGH | MEDIUM | P1 |
| Per-user statistics | MEDIUM | MEDIUM | P1 |
| User-submitted questions | MEDIUM | MEDIUM | P1 |
| Adaptive repetition | HIGH | HIGH | P2 |
| Admin review tooling | MEDIUM | MEDIUM | P2 |

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Practice drills | Standard quiz apps offer immediate correction | Anki offers repetition but weaker exam simulation | Telegram-first rapid drill with explanation |
| Exam simulation | Driving theory apps offer fixed exam sessions | Flashcard tools do not emulate scoring well | Native exam flow with fail threshold and final summary |
| Progress tracking | Apps often show raw percentages | Flashcards show review counts | Per-user accuracy plus most-failed questions |

## Sources

- https://github.com/donmerendolo/anki-carnet-conducir
- https://docs.python-telegram-bot.org/en/v21.0/index.html
- https://core.telegram.org/bots/api

---
*Feature research for: Telegram study bot for Spanish driving theory exam preparation*
*Researched: 2026-05-25*
