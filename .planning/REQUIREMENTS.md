# Requirements: BotCarnetConducir

**Defined:** 2026-05-25
**Core Value:** Practicar preguntas reales o equivalentes del carnet B desde Telegram de forma rápida, continua y con feedback útil sobre errores.

## v1 Requirements

### Platform

- [ ] **PLAT-01**: User can start the bot and access a main menu in Telegram.
- [ ] **PLAT-02**: User can navigate core actions using Telegram buttons without remembering commands.
- [ ] **PLAT-03**: User can resume an interrupted active exam session after bot restart or reconnect.

### Question Bank

- [ ] **BANK-01**: System can import permiso B questions from a local editable copy of the upstream dataset.
- [ ] **BANK-02**: Each imported question stores prompt, three answer options, explanation, source metadata, and optional image reference.
- [ ] **BANK-03**: System can distinguish imported questions from user-submitted questions.
- [ ] **BANK-04**: User can browse the question bank from Telegram and view question detail with explanation and image when available.

### Practice

- [ ] **PRAC-01**: User can start an infinite practice session from Telegram.
- [ ] **PRAC-02**: User can answer a practice question using inline buttons.
- [ ] **PRAC-03**: User receives immediate feedback showing whether the selected answer was correct.
- [ ] **PRAC-04**: User can read the explanation for the question after answering.
- [ ] **PRAC-05**: User can continue to the next practice question without returning to the main menu.

### Exam

- [ ] **EXAM-01**: User can start a full exam session for permiso B from Telegram.
- [ ] **EXAM-02**: Exam session tracks asked questions, selected answers, and current mistake count.
- [ ] **EXAM-03**: User sees progress during the exam, including current question number and accumulated errors.
- [ ] **EXAM-04**: System marks the exam as failed when the user finishes with more than three incorrect answers.
- [ ] **EXAM-05**: User receives a final exam summary with total correct, total incorrect, and pass/fail result.

### Contributions

- [ ] **CONT-01**: Any Telegram user can submit a new question proposal from the bot.
- [ ] **CONT-02**: Submitted question proposal captures prompt, answer options, intended correct answer, optional explanation, and optional image reference or upload.
- [ ] **CONT-03**: Submitted question proposal is stored with author metadata and review status.

### Statistics

- [ ] **STAT-01**: System records every answered practice question per user.
- [ ] **STAT-02**: System records every answered exam question per user.
- [ ] **STAT-03**: User can view personal totals of correct and incorrect answers.
- [ ] **STAT-04**: User can view accuracy summary for practice and exams separately.
- [ ] **STAT-05**: User can view the questions they miss most often or a list of recent mistakes.

## v2 Requirements

### Study Enhancements

- **STDY-01**: User receives adaptive repetition based on weak topics.
- **STDY-02**: User can filter practice by topic, sign type, or failure history.

### Operations

- **OPER-01**: Maintainer can review and approve or reject user-submitted questions from a dedicated admin workflow.
- **OPER-02**: System can sync deltas from upstream dataset automatically.

### Expansion

- **EXP-01**: User can switch between permiso B and other permits such as A1 or D.
- **EXP-02**: User can use a companion web dashboard.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Public web interface | User confirmed Telegram-only v1 |
| Multi-permit support | Scope intentionally limited to carnet B |
| AI-generated canonical questions | Quality and legal trust risk |
| Real-time upstream sync | Local editable copy is the chosen source of truth |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PLAT-01 | Phase 1 | Pending |
| PLAT-02 | Phase 1 | Pending |
| PLAT-03 | Phase 1 | Pending |
| BANK-01 | Phase 1 | Pending |
| BANK-02 | Phase 1 | Pending |
| BANK-03 | Phase 1 | Pending |
| BANK-04 | Phase 1 | Pending |
| PRAC-01 | Phase 1 | Pending |
| PRAC-02 | Phase 1 | Pending |
| PRAC-03 | Phase 1 | Pending |
| PRAC-04 | Phase 1 | Pending |
| PRAC-05 | Phase 1 | Pending |
| EXAM-01 | Phase 1 | Pending |
| EXAM-02 | Phase 1 | Pending |
| EXAM-03 | Phase 1 | Pending |
| EXAM-04 | Phase 1 | Pending |
| EXAM-05 | Phase 1 | Pending |
| CONT-01 | Phase 1 | Pending |
| CONT-02 | Phase 1 | Pending |
| CONT-03 | Phase 1 | Pending |
| STAT-01 | Phase 1 | Pending |
| STAT-02 | Phase 1 | Pending |
| STAT-03 | Phase 1 | Pending |
| STAT-04 | Phase 1 | Pending |
| STAT-05 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-25*
*Last updated: 2026-05-25 after initial definition*
