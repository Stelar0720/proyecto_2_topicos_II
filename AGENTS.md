# Instrucciones de Plaza Reserva

Lee `specs/constitution.md`, `specs/outcomes.md`, `specs/requirements.md`,
`specs/business-rules.md`, `specs/api.md`, `specs/acceptance-criteria.md` y
`specs/tasks.md` antes de editar. Consulta tu handoff en `docs/handoff/`.

- Implementa únicamente la historia asignada, de punta a punta (vista, API,
  lógica, persistencia y pruebas que correspondan). No reconstruyas la base.
- Si cambia un contrato, actualiza primero su especificación y coordina con Jack.
- Deriva las pruebas de los criterios; compara el resultado con la especificación.
- Mantén cambios y PR pequeños. Incluye IDs de tarea y criterios, comandos y resultados reales.
- No inventes entrevistas, evidencia, aprobaciones, métricas ni actividad de Git.
- Informa contradicciones que bloqueen la implementación; no las resuelvas silenciosamente.
- Coordina con su responsable antes de modificar archivos compartidos: modelos,
  migraciones, configuración, autenticación, `main.py`, layout, dependencias y contratos.
- Jack coordina migraciones e integración; Alex coordina CI. Cada autor prueba sus historias.
- No registres secretos, contraseñas, cookies ni códigos privados en logs o commits.
- No implementes recargos, incidencias, recuperación por placa ni reconocimiento automático.
- Parte del commit de la base integrado en `main`, actualiza tu copia y crea tu rama.
  Si todavía no está integrado, puedes revisar contratos; no empieces una historia dependiente.
- No fusiones PR, cambies protección de ramas ni publiques servicios por iniciativa propia.

Comandos y limitaciones reales: `README.md` y `docs/testing.md`.
