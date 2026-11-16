# Trazabilidad inicial

`previsto` = aún sin implementar; pruebas escritas no significan pruebas aprobadas.
Resultados reales en testing/verification; PR, commits y URLs solo cuando existan.

| Outcome | Requisito / reglas | Tarea | Código | Prueba / evidencia |
|---|---|---|---|---|
| OUT-05 | RNF-04 | BASE-01 | specs/, docs/ | lectura fuentes y verificación documental |
| OUT-05 | RNF-04 | BASE-02 | cli.py, models.py, migrations/0001 | test_seed_idempotent_preserves_existing; test_migration_matches_models_and_downgrades; ejecución pendiente |
| OUT-02/03/04 | RF-08, BR-28/30 | BASE-02 | auth.py, security.py, main.py | test_unauthorized, test_login_expiry_and_revocation, test_origin_and_invalid_credentials; ejecución pendiente |
| OUT-01 | RF-01/02, BR-01–04/11/13–15 | HU-01, T-01A–C | `reservations.py`, `templates/reservations/`, `tests/test_reservations.py` | AC-01/02/03/07/13 verificados en rama `feature/hu-01-reservas`; PR pendiente de revisión humana (ver evidencia HU-01) |
| OUT-01 | RF-03, BR-03/04/06/29/30 | HU-02, T-02A/B | `reservations.py` (consulta/cancelación previstas) | AC-04/08/13 pendientes |
| OUT-02 | RF-04/05, BR-05–17 | HU-03, T-03A/B | entries.py previsto | AC-05–08/13 pendientes |
| OUT-03 | RF-06, BR-17–23 | HU-04, T-04A/B | exits.py previsto | AC-09–11/13 pendientes |
| OUT-04 | RF-07, BR-24–28 | HU-05, T-05A | alerts.py previsto | AC-12/13 pendientes |
| OUT-05 | RNF-01/04 | QA-01, T-QA1/2 | demo.py, integration/ previstos | AC-14 e integración pendientes |
| OUT-05 | RNF-04 | ENTREGA-01 | CI/README/config publicación posterior | ensayo y despliegue pendientes |

Al completar cada PR añadir hash/URL real y resultados concretos, sin convertir
esta tabla en historial ficticio. Cambios: conservar solicitud real → revisión de
spec/criterios/tareas → diff de código/pruebas → resultado → aceptación humana real.

## Evidencia HU-01 (rama `feature/hu-01-reservas`, sin revisión humana)

Ejecutado el 2026-11-16 en esta sesión; resultados reales, no aprobación.

| Comprobación | Resultado |
|---|---|
| `pytest` con SQLite de archivo | 33 passed |
| `pytest` con `TEST_POSTGRES_URL` (PostgreSQL 17 descartable `_test`) | 62 passed |
| AC-02 carrera del último preferencial | dos conexiones independientes: una reserva, la otra 409 `CATEGORY_FULL`, 20 reservas y 20 asignaciones, sin filas parciales |
| AC-07 misma placa simultánea | una reserva, la otra 409 `PLATE_BUSY` |
| AC-03 vencimiento exacto | a `expires_at` la disponibilidad vuelve a 20 y la base sigue `pending`; la misma placa puede reservar de nuevo liberando dentro del bloqueo |
| QR (AC-01) | SVG en la vista decodificado con `zbarimg` devuelve exactamente el código privado, sin placa |
| Vista /reservar | Chromium real: 20/80 iniciales, reserva P020 con vencimiento en America/Panama, 409 visible por placa duplicada, categoría llena sin formulario |

Decisiones aplicadas como propuesta pendiente de Product/Spec: D-03 y D-04. La
petición `POST` de formulario requirió corregir `same_origin` para aceptar
`Sec-Fetch-Site: same-origin`, porque `Referrer-Policy: no-referrer` hace que Chrome
envíe `Origin: null` en formularios del mismo origen (verificado con sonda propia).
