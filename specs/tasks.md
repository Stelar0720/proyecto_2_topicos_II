# Tareas y dependencias

Estado GitHub no inferido: consultar `docs/github-project-setup.md` y `docs/github-state.json`.
La preparación local no es actividad publicada ni revisión humana.

| ID | Entrega / responsable previsto | Dependencias | Criterios / módulos | Condición de terminado |
|---|---|---|---|---|
| BASE-01 | outcomes/specs, Jack | fuentes | specs/, docs/; OUT-01–05, AC-S01 | coherencia revisada, backlog trazable |
| BASE-02 | base compartida, Jack | BASE-01 | src/, migrations/, tests/; AC-B01–B06 | pruebas ejecutadas y PR revisado/integrado |
| HU-01 | disponibilidad/reserva QR, Francisco | BASE-02 integrado | reservations.py, templates/reservations/, tests/test_reservations.py; AC-01/02/03/07/13 | historia completa, carrera verificada |
| HU-02 | consulta/cancelación, Francisco | HU-01 | mismo módulo + pruebas privadas; AC-04/08/13 | liberar y privacidad verificadas |
| HU-03 | ingresos/ticket, Francisco | HU-01/02 | entries.py, templates/entries/, tests/test_entries.py; AC-05–08/13 | conversión atómica y ticket imprimible verificados |
| HU-04 | salida/cobro/pago, Alex | HU-03 | exits.py, templates/exits/, tests/test_exits.py; AC-09–11/13 | cierre/pago único con reloj y reintentos |
| HU-05 | alerta >24h, Alex | HU-03 | alerts.py, templates/alerts/, tests/test_alerts.py; AC-12/13 | tres fronteras temporales verificadas |
| QA-01 | demo/integración, Alex | HU-01–05 | demo.py, tests/integration/; AC-14 y escenarios críticos | carga idempotente separada y evidencia reproducible |
| ENTREGA-01 | ejecución/publicación-demo, Jack + Alex | QA-01 | README, CI, docs/testing.md | ensayo reproducible, PG probado, URL/evidencia real |
| DEMO-UX | cuentas cliente, reserva programada, QR único y dashboard | HU-01–05 | migración sucesora, auth, reservas, garita, salida, dashboard; AC-15–17 | demo local con controles de roles y pruebas |

Subtareas pequeñas **dentro de cada historia**, no entregas aisladas:

- T-01A: HU-01, consulta efectiva y vista de disponibilidad (AC-03); dep BASE-02.
- T-01B: HU-01, reserva transaccional + QR privado + errores (AC-01/07); dep T-01A.
- T-01C: HU-01, carrera último cupo/rollback/seguridad y evidencia; dep T-01B.
- T-02A: HU-02, consulta privada + vista (AC-04); dep HU-01.
- T-02B: HU-02, cancelación/repetición/vencimiento + pruebas (AC-04/08); dep T-02A.
- T-03A: HU-03, ingreso reservado atómico + interfaz/pruebas (AC-05/08); dep HU-02.
- T-03B: HU-03, espontáneo/ticket/impresión + carrera (AC-06/07); dep T-03A.
- T-04A: HU-04, cotización temporal en centavos + vista/pruebas (AC-09); dep HU-03.
- T-04B: HU-04, pago/cierre idempotente + interfaz/pruebas (AC-10/11); dep T-04A.
- T-05A: HU-05, consulta/vista de alerta sin efectos + pruebas (AC-12); dep HU-03.
- T-QA1: seis escenarios demo con reloj común/base separada (AC-14); dep HU-01–05.
- T-QA2: integración y carreras en SQLite/PostgreSQL con evidencia; dep T-QA1.

Archivos de historias son **previstos**, no rutas ya existentes. La composición en
main.py y cualquier cambio de esquema se coordina con Jack. DoD común: criterio
verificado, código/prueba/documentación trazados, ningún secreto, PR revisado y
aceptación humana registrada antes de marcar Terminado.
