# Pitfalls Research

**Domain:** Telegram study bot for Spanish driving theory exam preparation
**Researched:** 2026-05-25
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Dirty Upstream Import

**What goes wrong:**
Imported questions keep upstream quirks, broken line breaks, missing explanations, or malformed correct-answer encoding.

**Why it happens:**
Developers use the source JSON as if it were production-ready schema.

**How to avoid:**
Build a normalization layer with validation, provenance fields, and importer reports.

**Warning signs:**
Different question records require handler-specific exceptions.

**Phase to address:**
Phase 1

---

### Pitfall 2: Losing Exam State on Restart

**What goes wrong:**
Users are midway through an exam and the bot forgets progress after a deployment or crash.

**Why it happens:**
Conversation state is kept only in memory.

**How to avoid:**
Persist active sessions, question order, current index, and mistakes in the database.

**Warning signs:**
Exam logic depends on process globals or `context.user_data` alone.

**Phase to address:**
Phase 2 and Phase 3

---

### Pitfall 3: User Contributions Poison the Main Bank

**What goes wrong:**
Incorrect or duplicate user-submitted questions appear in practice or exams.

**Why it happens:**
There is no source/status separation between imported and user-created content.

**How to avoid:**
Store source, author, review status, and activation flags for every question.

**Warning signs:**
There is only one `questions` bucket and no moderation metadata.

**Phase to address:**
Phase 4

---

### Pitfall 4: Telegram UX Becomes Chat Spam

**What goes wrong:**
Every answer sends several long messages, making the bot tiring to use.

**Why it happens:**
The design does not treat Telegram as a constrained conversational interface.

**How to avoid:**
Use concise prompts, inline keyboards, and compact feedback messages with optional detail expansion.

**Warning signs:**
Core flows need scrolling through many messages to continue.

**Phase to address:**
Phase 2 and Phase 3

---

### Pitfall 5: Legal/Distribution Ambiguity Around Source Content

**What goes wrong:**
The bot ships imported data and images without clarifying licensing or attribution obligations.

**Why it happens:**
Content ingestion is treated as a technical detail instead of a product dependency.

**How to avoid:**
Document provenance, license, and image acquisition path from the first import phase.

**Warning signs:**
There is no metadata or docs linking imported records to their source.

**Phase to address:**
Phase 1 and Phase 6

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip migrations and recreate DB manually | Faster start | Schema drift and lost data | Never after first persisted prototype |
| Keep stats as only aggregate counters | Simple writes | No way to add richer analytics later | Acceptable only for throwaway experiments |
| Reuse one handler for all flows | Less code initially | Tangled state transitions and bugs | Never for exam + submissions together |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Telegram Bot API | Assuming message order/state is always linear | Persist explicit session state and validate callbacks |
| Upstream dataset | Depending on remote repo shape at runtime | Import into canonical local storage |
| Media assets | Assuming every question image exists locally | Validate references and support no-image fallback |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Random question selection by full table scan | Slower drills as bank grows | Precompute candidate sets or use indexed selection | Around a few thousand questions plus stats joins |
| Recomputing all user stats on each request | Slow stats screens | Maintain answer events plus cached aggregates | With active repeat users |
| Large image resend on every retry | Chat feels sluggish | Cache media identifiers or local references | On image-heavy practice flows |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Trusting raw user text as ready-to-publish question content | Low-quality or malicious content in canonical bank | Validate, sanitize, and isolate submissions |
| Logging full bot token or secrets | Bot takeover | Use env vars and redacted logs |
| Missing rate controls on submission endpoints | Spam and DB pollution | Add basic throttling and per-user limits |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Long command list instead of a simple menu | Users forget how to navigate | Start with a persistent main menu |
| Showing explanations before the user answers | Ruins study loop | Reveal explanation only after answer |
| No progress indicator in exams | Users feel lost | Show question number and current mistakes |

## "Looks Done But Isn't" Checklist

- [ ] **Importer:** Often missing image-reference handling — verify missing-media strategy
- [ ] **Practice mode:** Often missing per-answer logging — verify stats update after every answer
- [ ] **Exam mode:** Often missing resume-safe state — verify restart mid-exam
- [ ] **Question submissions:** Often missing provenance fields — verify imported vs user-created separation

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Dirty upstream import | MEDIUM | Re-run importer on clean schema and preserve source mapping |
| Lost exam state | HIGH | Add session persistence and invalidate broken sessions explicitly |
| Polluted question bank | HIGH | Deactivate affected records by source/status and rebuild canonical subsets |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Dirty upstream import | Phase 1 | Imported sample rows are normalized and queryable |
| Losing exam state on restart | Phase 3 | Restart simulation preserves or safely closes exam |
| User contributions poison the main bank | Phase 4 | Practice/exam queries exclude inactive submissions |
| Telegram UX becomes chat spam | Phase 2 | Core loops fit into compact message exchanges |
| Legal/distribution ambiguity | Phase 6 | Docs include provenance and release checklist |

## Sources

- https://github.com/donmerendolo/anki-carnet-conducir
- https://docs.python-telegram-bot.org/en/v21.0/index.html
- https://core.telegram.org/bots/api

---
*Pitfalls research for: Telegram study bot for Spanish driving theory exam preparation*
*Researched: 2026-05-25*
