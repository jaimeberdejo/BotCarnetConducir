# Roadmap: BotCarnetConducir

## Overview

El roadmap se ejecutará como una sola macro fase para intentar entregar el MVP completo de una pasada. La descomposición fina se mantiene a nivel de planes internos para conservar orden, validación y capacidad de seguimiento sin repartir el trabajo en varias fases.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: MVP One Shot** - Bot completo de Telegram para practicar, examinar, consultar banco, proponer preguntas y ver estadísticas.

## Phase Details

### Phase 1: MVP One Shot
**Goal**: Entregar el MVP completo del bot de Telegram para carnet B con importación de contenido, práctica, examen, consulta de banco, aportaciones de usuarios, estadísticas y endurecimiento mínimo de publicación.
**Depends on**: Nothing (first phase)
**Requirements**: [PLAT-01, PLAT-02, PLAT-03, BANK-01, BANK-02, BANK-03, BANK-04, PRAC-01, PRAC-02, PRAC-03, PRAC-04, PRAC-05, EXAM-01, EXAM-02, EXAM-03, EXAM-04, EXAM-05, CONT-01, CONT-02, CONT-03, STAT-01, STAT-02, STAT-03, STAT-04, STAT-05]
**Success Criteria** (what must be TRUE):
  1. Un usuario puede abrir el bot y usar un menú principal claro para entrar en práctica, examen, banco, estadísticas y aportación de preguntas.
  2. El sistema importa y sirve correctamente el banco local del permiso B, resolviendo preguntas con y sin imagen desde la carpeta `Imagenes/`.
  3. Un usuario puede practicar preguntas infinitas con feedback inmediato y explicación, y puede completar un examen con resultado correcto de aprobado o suspenso por más de tres fallos.
  4. Un usuario puede consultar preguntas del banco, enviar nuevas propuestas y ver sus estadísticas personales de aciertos y errores.
  5. El sistema persiste sesiones, respuestas y procedencia del contenido, y queda suficientemente documentado para despliegue inicial.
**Plans**: 6 plans

Plans:
- [ ] 01-01: Inicializar proyecto Python, configuración, dependencias y estructura de carpetas
- [ ] 01-02: Diseñar esquema de datos, migraciones y repositorios base
- [ ] 01-03: Implementar importador de preguntas B, imágenes y validación de contenido
- [ ] 01-04: Construir bot de Telegram con menú principal y flujo de práctica infinita
- [ ] 01-05: Implementar exámenes, consulta de banco, envío de preguntas y estadísticas
- [ ] 01-06: Endurecer persistencia, pruebas, logging y documentación de despliegue/licencia

## Progress

**Execution Order:**
Phases execute in numeric order: 1

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. MVP One Shot | 0/6 | Not started | - |
