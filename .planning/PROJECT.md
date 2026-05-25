# BotCarnetConducir

## What This Is

Bot de Telegram para practicar el examen teórico del permiso B en España. Permite responder preguntas de forma infinita, hacer exámenes tipo DGT con criterio de suspenso por más de tres fallos, consultar el banco de preguntas, proponer nuevas preguntas y ver estadísticas personales de aciertos y errores.

El producto está orientado a estudiantes que preparan el carnet B y quieren practicar desde Telegram sin depender de una app web o de Anki.

## Core Value

Practicar preguntas reales o equivalentes del carnet B desde Telegram de forma rápida, continua y con feedback útil sobre errores.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Practicar preguntas infinitas desde Telegram con respuesta inmediata y explicación.
- [ ] Realizar exámenes completos tipo carnet B con suspenso al superar tres fallos.
- [ ] Importar y mantener una copia propia editable del banco de preguntas e imágenes del dataset fuente.
- [ ] Consultar el banco de preguntas y permitir que cualquier usuario proponga nuevas preguntas.
- [ ] Mostrar estadísticas por usuario sobre preguntas acertadas y equivocadas.

### Out of Scope

- Panel web de administración o estudio — el alcance confirmado es solo bot de Telegram.
- Soporte para permisos A1, D u otros — v1 se limita al permiso B en España.
- Sincronización en tiempo real con el repositorio externo — se trabajará con una copia propia importada para poder editar y versionar el banco.
- Generación automática de nuevas preguntas con IA como fuente principal — arriesga calidad normativa y deriva pedagógica.

## Context

El producto parte de un banco inicial externo: `donmerendolo/anki-carnet-conducir`, que publica decks de Anki para permisos españoles. El README del repositorio indica que el permiso B estaba actualizado el 2025-02-25 y contiene 2.890 preguntas, con un fichero `data/data_B.json` y un flujo separado para imágenes. El JSON de ejemplo contiene pregunta, tres respuestas, explicación, imagen opcional y una codificación de respuesta correcta.

La experiencia principal debe funcionar en un chat de Telegram privado, con navegación por botones, continuidad de sesión y mensajes cortos. El usuario debe poder estudiar sin fricción: empezar práctica, contestar, ver si acertó, entender por qué y seguir.

Hay dos tensiones de diseño importantes:
- calidad del contenido: al permitir aportaciones de cualquier usuario, el banco debe distinguir claramente entre preguntas importadas y preguntas propuestas por usuarios;
- trazabilidad legal y operativa: el dataset fuente usa licencia GPL-3.0 y las imágenes están documentadas en el README como descarga separada, así que la importación y redistribución deben tratarse explícitamente.

## Constraints

- **Platform**: Solo Telegram bot — el usuario descartó panel web en v1.
- **Domain**: Permiso B, España — el producto debe hablar el lenguaje y reglas del examen español.
- **Content Source**: Importación inicial desde `anki-carnet-conducir` — reduce coste inicial y acelera MVP.
- **Licensing**: Dependencia de contenido con GPL-3.0 — obliga a revisar distribución y atribución antes de publicar.
- **Media Pipeline**: Imágenes asociadas no están completas en el repo principal — el importador debe tolerar preguntas sin imagen y gestionar medios por separado.
- **Quality**: Preguntas añadidas por usuarios no deben degradar el examen principal — deben persistirse con metadatos de origen y estado.
- **UX**: Flujo conversacional corto y claro — Telegram penaliza interfaces largas o ambiguas.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bot solo en Telegram para v1 | El alcance confirmado excluye panel web y prioriza velocidad de entrega | — Pending |
| Fuente inicial = copia propia importada del repo externo | Permite editar, versionar y corregir el banco sin depender del upstream | — Pending |
| Alcance inicial limitado a carnet B España | Reduce complejidad de contenido, validación y UX | — Pending |
| Las preguntas propuestas por usuarios se guardan con origen propio y no sustituyen automáticamente el dataset importado | Evita contaminar el banco principal y preserva confianza pedagógica | — Pending |
| Las estadísticas serán por usuario y por pregunta | Es la base mínima para feedback útil y repetición espaciada futura | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-25 after initialization*
