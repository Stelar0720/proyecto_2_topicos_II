# Trazabilidad inicial

`previsto` = aún sin implementar; pruebas escritas no significan pruebas aprobadas.
Resultados reales en testing/verification; PR, commits y URLs solo cuando existan.

| Outcome | Requisito / reglas | Tarea | Código | Prueba / evidencia |
|---|---|---|---|---|
| OUT-05 | RNF-04 | BASE-01 | specs/, docs/ | lectura fuentes y verificación documental |
| OUT-05 | RNF-04 | BASE-02 | cli.py, models.py, migrations/0001 | test_seed_idempotent_preserves_existing; test_migration_matches_models_and_downgrades; ejecución pendiente |
| OUT-02/03/04 | RF-08, BR-28/30 | BASE-02 | auth.py, security.py, main.py | test_unauthorized, test_login_expiry_and_revocation, test_origin_and_invalid_credentials; ejecución pendiente |
| OUT-01 | RF-01/02, BR-01–04/11/13–15 | HU-01, T-01A–C | reservations.py previsto | AC-01/02/03/07/13; carreras pendientes |
| OUT-01 | RF-03, BR-03/04/06/29/30 | HU-02, T-02A/B | reservations.py previsto | AC-04/08/13 pendientes |
| OUT-02 | RF-04/05, BR-05–17 | HU-03, T-03A/B | entries.py previsto | AC-05–08/13 pendientes |
| OUT-03 | RF-06, BR-17–23 | HU-04, T-04A/B | exits.py previsto | AC-09–11/13 pendientes |
| OUT-04 | RF-07, BR-24–28 | HU-05, T-05A | alerts.py previsto | AC-12/13 pendientes |
| OUT-05 | RNF-01/04 | QA-01, T-QA1/2 | demo.py, integration/ previstos | AC-14 e integración pendientes |
| OUT-05 | RNF-04 | ENTREGA-01 | CI/README/config publicación posterior | ensayo y despliegue pendientes |

Al completar cada PR añadir hash/URL real y resultados concretos, sin convertir
esta tabla en historial ficticio. Cambios: conservar solicitud real → revisión de
spec/criterios/tareas → diff de código/pruebas → resultado → aceptación humana real.
