# Handoff de Francisco

La base está preparada localmente. **Esperar integración real de BASE-02 en main**
y revisar `docs/github-state.json` para saber si existen issues/Project/PR. No
interpretar este documento como autorización de integración ni como aprobación.

## Miniprompt copiable para tu Codex

```text
Trabaja en el repositorio proyecto_2_topicos_II, Plaza Reserva, como apoyo de Francisco.
Lee AGENTS.md, README.md, specs/constitution.md, outcomes.md, requirements.md,
business-rules.md, architecture.md, data-model.md, api.md, acceptance-criteria.md,
tasks.md y docs/testing.md, team-plan.md y traceability.md.

Primero comprueba git status y conserva cambios locales. Comprueba que BASE-02
esté integrado en main y parte de ese commit real: git fetch origin, git switch main,
git pull --ff-only origin main. Solo con copia limpia crea feature/hu-01-reservas.
Si la base no está integrada, informa la dependencia y limita trabajo a revisión.
No reconstruyas el esqueleto, no crees otro tablero ni dupliques issues.

Responsabilidad: HU-01 (T-01A/B/C), luego HU-02 (T-02A/B), luego HU-03 (T-03A/B),
un PR por historia completa. Consulta el registro GitHub; si falta URL, usa los IDs
de specs/tasks.md, no inventes números de issue. Tu usuario GitHub todavía no se conoce.

HU-01: disponibilidad efectiva, reserva preferencial de 30 minutos, QR digital y código.
HU-02: consulta/cancelación privadas, liberación, estados terminales.
HU-03: ingreso reservado atómico y espontáneo general, QR/ticket imprimible.
Cada historia incluye vista, endpoint, servicio, persistencia y pruebas pertinentes.
Respeta contratos propuestos /api/availability, /api/reservations,
/api/reservations/lookup, /api/reservations/cancel,
/api/entries/reservation y /api/entries/walk-in; hoy NO existen.
Discute D-03/D-04/D-05 con Product/Spec antes de implementarlos, sin inventar confirmación.

Base existente: src/plaza_reserva/{main,config,db,clock,models,auth,security,errors,cli}.py,
templates/base.html y static/app.css. Usa allocation_transaction con sesión nueva
para asignaciones/cancelaciones/conversión; dentro libera reservas vencidas y valida.
Clock.now() una vez por operación, UTC en BD, America/Panama en vistas. No dependas
de cron. UNIQUE/FK de allocations + índices parciales no sustituyen la transacción.
PBKDF2/sesiones del personal existentes; current_staff y require_roles protegen rutas.
same_origin protege mutaciones. QR/códigos privados de 32 bytes aleatorios, digest
en BD, sin placa en QR, sin secretos en logs ni querystrings. Código manual alternativo.
Errores 401/403/404/409/422/503 y envelope en specs/api.md.

Agrega módulos previstos reservations.py, entries.py, templates/reservations/ y
templates/entries/, pruebas test_reservations.py/test_entries.py. Estos archivos
no existen aún; créalos solo con su historia. Coordina main.py para montar routers.
Archivos compartidos de Jack: models, migraciones, db/config/auth/security/clock,
main, cli, layout, CSS, dependencias y specs. No modificarlos sin coordinación.
No edites migración 0001 tras integración; cualquier cambio lleva sucesora coordinada.

Prueba AC-01–08/13: último cupo, dos conexiones simultáneas, placa duplicada,
expiración exacta sin cron, rollback, conversión, QR reutilizado, cancelación,
privacidad y roles. Ejecuta python -m pytest en entorno instalado; para PostgreSQL
usa TEST_POSTGRES_URL a BD descartable terminada _test. Reporta resultados reales.
No implementes salidas/cobros/alertas de Alex ni recargos/incidencias/ALPR.

Git: commits pequeños con ID, push de tu rama, PR a main con criterios y evidencia.
Actualiza spec si cambia contrato, traceability y ai-log. En revisión no equivale
a terminado; no inventes revisiones ni fusiones ni cierres. No fusiones el PR.
```
