# Project Research Summary

**Project:** BotCarnetConducir
**Domain:** Telegram study bot for Spanish driving theory exam preparation
**Researched:** 2026-05-25
**Confidence:** MEDIUM

## Executive Summary

Este proyecto encaja mejor como un bot Python monolítico con persistencia relacional simple y un importador offline del banco de preguntas. La complejidad real no está en Telegram sino en mantener un modelo canónico de preguntas, sesiones persistentes para exámenes y una separación estricta entre contenido importado y contenido enviado por usuarios.

La recomendación es construir primero la base de datos e importación del permiso B, después el flujo de práctica, luego el motor de examen y finalmente las aportaciones de usuarios y estadísticas. El riesgo principal no es técnico sino de calidad de contenido y trazabilidad: si el dataset se importa sin normalización o las preguntas de usuarios se mezclan con el banco principal, el producto pierde confianza rápidamente.

## Key Findings

### Recommended Stack

Python 3.12 con `python-telegram-bot` 21.x y SQLite es una base pragmática para MVP. Permite iterar rápido, persistir sesiones y mantener el código en una sola app desplegable. SQLAlchemy y Alembic reducen deuda temprana en un dominio con varias entidades relacionadas: preguntas, respuestas, sesiones de examen, estadísticas y aportaciones.

**Core technologies:**
- Python: runtime principal — rápido para bot, importadores y reglas
- python-telegram-bot: integración Telegram — conversación, callbacks, media y persistencia
- SQLite: almacenamiento MVP — suficiente y simple
- SQLAlchemy: capa de acceso a datos — estructura y futura migración

### Expected Features

**Must have (table stakes):**
- Práctica con corrección inmediata — los usuarios esperan estudiar pregunta a pregunta
- Examen con puntuación final — imprescindible para simular el teórico
- Soporte de imágenes — parte del contenido depende de señales y escenas
- Estadísticas por usuario — necesario para medir progreso

**Should have (competitive):**
- Flujo de práctica infinita natural en Telegram
- Aportación de nuevas preguntas por usuarios
- Estadísticas de errores más frecuentes

**Defer (v2+):**
- Repetición espaciada avanzada
- Soporte multi-permiso
- Panel web

### Architecture Approach

La arquitectura recomendada separa claramente capa Telegram, reglas de dominio y persistencia. El importador debe alimentar un modelo canónico de preguntas. Los motores de práctica y examen deben operar solo sobre ese modelo, nunca sobre el JSON original.

**Major components:**
1. Handlers de Telegram — navegación y captura de respuestas
2. Servicios de dominio — práctica, examen, estadísticas y aportaciones
3. Persistencia — banco de preguntas, sesiones activas y eventos de respuesta

### Critical Pitfalls

1. **Dirty upstream import** — normalizar el dataset antes de exponerlo
2. **Losing exam state on restart** — persistir sesiones activas
3. **User contributions poison the main bank** — separar por origen y estado
4. **Telegram UX becomes chat spam** — usar mensajes compactos e inline keyboards
5. **Legal/distribution ambiguity** — documentar licencia, origen e imágenes

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Data Foundation
**Rationale:** todo depende del banco canónico y de la persistencia
**Delivers:** esquema inicial, importador y contenido base
**Addresses:** importación, trazabilidad, persistencia base
**Avoids:** dirty upstream import

### Phase 2: Practice Flow
**Rationale:** es el bucle de valor más corto y valida el UX principal
**Delivers:** menú y práctica infinita
**Uses:** bot framework y question service
**Implements:** handlers y practice engine

### Phase 3: Exam Engine
**Rationale:** reutiliza pregunta/respuesta ya implementadas y añade estado persistente
**Delivers:** exámenes, scoring y resultado final

### Phase 4: Question Bank and Contributions
**Rationale:** se apoya en el modelo canónico ya estable
**Delivers:** consulta del banco y envío de nuevas preguntas

### Phase 5: Statistics and Feedback
**Rationale:** depende de eventos generados por práctica y exámenes
**Delivers:** métricas de usuario y preguntas con más fallo

### Phase 6: Hardening and Release Readiness
**Rationale:** cerrar calidad, medios, documentación y operativa antes de publicar
**Delivers:** robustez, documentación de licencia y despliegue

### Phase Ordering Rationale

- El importador y la persistencia van primero porque todo lo demás depende de ellos.
- La práctica precede al examen porque comparte la misma evaluación con menor complejidad de estado.
- Las estadísticas se dejan después de generar suficiente telemetría de respuestas.
- El endurecimiento final cubre riesgos legales, medios y operativos que no deben bloquear el primer desarrollo.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** licencia y flujo exacto de imágenes del dataset fuente
- **Phase 6:** estrategia de despliegue y cumplimiento de redistribución

Phases with standard patterns (skip research-phase):
- **Phase 2:** menús y callbacks básicos de Telegram
- **Phase 3:** scoring y persistencia simple de sesiones

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Stack muy estándar, pero versiones exactas pueden ajustarse al iniciar implementación |
| Features | HIGH | Alcance validado por el usuario |
| Architecture | MEDIUM | Sólida para MVP, pero la moderación de aportaciones puede evolucionar |
| Pitfalls | MEDIUM | Riesgos claros por naturaleza del producto y la fuente de datos |

**Overall confidence:** MEDIUM

### Gaps to Address

- Flujo exacto de obtención y empaquetado de imágenes del dataset
- Política definitiva para publicar o no preguntas de usuarios en el banco principal

## Sources

### Primary (HIGH confidence)
- https://github.com/donmerendolo/anki-carnet-conducir — estructura del repo, licencia, JSON y volumen del carnet B
- https://docs.python-telegram-bot.org/en/v21.0/index.html — capacidades base del framework
- https://core.telegram.org/bots/api — capacidades de botones y envío de medios

### Secondary (MEDIUM confidence)
- Inferencia arquitectónica a partir de patrones estándar para bots de estudio y apps de cuestionarios

---
*Research completed: 2026-05-25*
*Ready for roadmap: yes*
