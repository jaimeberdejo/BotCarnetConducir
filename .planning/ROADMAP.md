# Roadmap: BotCarnetConducir

## Overview

El roadmap construye primero la base de contenido y persistencia, después la experiencia principal de práctica y examen en Telegram, y por último añade aportaciones de usuarios, estadísticas y endurecimiento operativo para publicar el bot con confianza.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Data Foundation** - Esquema base, importador y banco canónico del carnet B.
- [ ] **Phase 2: Telegram Practice Loop** - Menú principal y práctica infinita con feedback inmediato.
- [ ] **Phase 3: Exam Engine** - Exámenes completos con persistencia de sesión y resultado final.
- [ ] **Phase 4: Bank Browsing and Contributions** - Consulta del banco y envío de nuevas preguntas.
- [ ] **Phase 5: User Statistics** - Métricas personales y errores frecuentes.
- [ ] **Phase 6: Hardening and Release** - Robustez, medios, documentación y preparación de despliegue.

## Phase Details

### Phase 1: Data Foundation
**Goal**: Crear la base técnica y de contenido para servir preguntas del carnet B desde un banco canónico local.
**Depends on**: Nothing (first phase)
**Requirements**: [BANK-01, BANK-02, BANK-03]
**Success Criteria** (what must be TRUE):
  1. Existe una base de datos inicial con preguntas del permiso B importadas desde la copia local del dataset fuente.
  2. Cada pregunta importada conserva en el sistema pregunta, respuestas, explicación, origen e imagen opcional.
  3. El modelo de datos separa claramente preguntas importadas de preguntas propuestas por usuarios.
  4. El proyecto puede arrancar configuración, persistencia y acceso al banco de preguntas sin depender del JSON original en runtime.
**Plans**: 3 plans

Plans:
- [ ] 01-01: Inicializar proyecto Python, configuración, dependencias y estructura de carpetas
- [ ] 01-02: Diseñar esquema de datos, migraciones y repositorios base
- [ ] 01-03: Implementar importador de preguntas B y validación de contenido

### Phase 2: Telegram Practice Loop
**Goal**: Entregar la experiencia principal de práctica infinita dentro de Telegram.
**Depends on**: Phase 1
**Requirements**: [PLAT-01, PLAT-02, PRAC-01, PRAC-02, PRAC-03, PRAC-04, PRAC-05]
**Success Criteria** (what must be TRUE):
  1. Un usuario puede abrir el bot y navegar desde un menú principal claro.
  2. Un usuario puede iniciar práctica infinita y responder usando botones de Telegram.
  3. Tras cada respuesta, el bot indica si fue correcta y muestra explicación.
  4. El usuario puede continuar a la siguiente pregunta sin reiniciar el flujo.
**Plans**: 3 plans

Plans:
- [ ] 02-01: Construir entrypoint del bot, menús y navegación base
- [ ] 02-02: Implementar selección de preguntas y evaluación de respuestas en práctica
- [ ] 02-03: Afinar UX de mensajes, botones e imágenes en práctica

### Phase 3: Exam Engine
**Goal**: Añadir simulación de examen completa con estado persistente y criterio de aprobado/suspenso.
**Depends on**: Phase 2
**Requirements**: [PLAT-03, EXAM-01, EXAM-02, EXAM-03, EXAM-04, EXAM-05]
**Success Criteria** (what must be TRUE):
  1. Un usuario puede iniciar un examen y responder un conjunto completo de preguntas.
  2. El bot conserva el progreso del examen, número de errores y respuestas dadas durante la sesión.
  3. El usuario ve su progreso y errores acumulados durante el examen.
  4. Al terminar, el bot informa correctamente si aprueba o suspende con más de tres fallos.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Modelar sesiones de examen y persistencia de estado
- [ ] 03-02: Implementar flujo de examen, scoring y resumen final
- [ ] 03-03: Verificar recuperación ante reinicios e interrupciones

### Phase 4: Bank Browsing and Contributions
**Goal**: Permitir transparencia sobre el banco de preguntas y captura estructurada de nuevas propuestas de usuarios.
**Depends on**: Phase 3
**Requirements**: [BANK-04, CONT-01, CONT-02, CONT-03]
**Success Criteria** (what must be TRUE):
  1. Un usuario puede consultar preguntas del banco desde Telegram.
  2. Una propuesta de nueva pregunta puede capturarse paso a paso desde el bot.
  3. Cada propuesta queda guardada con autor, contenido y estado de revisión.
  4. Las preguntas propuestas no aparecen por error en práctica o examen canónico.
**Plans**: 3 plans

Plans:
- [ ] 04-01: Implementar consulta y visualización de banco de preguntas
- [ ] 04-02: Implementar conversación de alta de preguntas de usuarios
- [ ] 04-03: Persistir metadatos de origen, estado y validaciones

### Phase 5: User Statistics
**Goal**: Dar feedback útil a cada usuario sobre rendimiento y errores frecuentes.
**Depends on**: Phase 4
**Requirements**: [STAT-01, STAT-02, STAT-03, STAT-04, STAT-05]
**Success Criteria** (what must be TRUE):
  1. Cada respuesta de práctica y examen queda registrada por usuario.
  2. Un usuario puede ver sus totales de aciertos y errores.
  3. Un usuario puede ver precisión separada para práctica y examen.
  4. El bot puede mostrar errores recientes o preguntas más falladas por el usuario.
**Plans**: 2 plans

Plans:
- [ ] 05-01: Registrar eventos de respuesta y agregados por usuario
- [ ] 05-02: Exponer pantallas o mensajes de estadísticas en Telegram

### Phase 6: Hardening and Release
**Goal**: Cerrar riesgos operativos, de medios y de distribución para dejar el bot listo para desplegar.
**Depends on**: Phase 5
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. El bot gestiona preguntas con y sin imagen de forma robusta.
  2. Existen pruebas suficientes sobre importador, scoring y flujos críticos.
  3. La documentación de despliegue, configuración y procedencia/licencia del contenido está escrita.
  4. El proyecto tiene un camino claro de publicación y operación básica.
**Plans**: 3 plans

Plans:
- [ ] 06-01: Endurecer manejo de medios, errores y logging
- [ ] 06-02: Añadir pruebas automatizadas y checks de calidad
- [ ] 06-03: Documentar despliegue, configuración y cumplimiento de contenido

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Foundation | 0/3 | Not started | - |
| 2. Telegram Practice Loop | 0/3 | Not started | - |
| 3. Exam Engine | 0/3 | Not started | - |
| 4. Bank Browsing and Contributions | 0/3 | Not started | - |
| 5. User Statistics | 0/2 | Not started | - |
| 6. Hardening and Release | 0/3 | Not started | - |
