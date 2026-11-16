# Auditoría de entrega - Plaza Reserva

Fecha de auditoría: 2026-11-16. Alcance: evidencia local disponible del
repositorio; no se publicó, fusionó ni desplegó nada durante esta auditoría.

## Fuente y método

La guía principal revisada fue `DSaIA-Proyecto2.pdf` (3 páginas). Exige el
recorrido ODD -> SDD -> código -> pruebas -> resultado, Git con ramas y revisión,
IA documentada, cambio de requisito trazable y, como mínimo, una prueba
automatizada de no doble reserva. Se revisaron `README.md`, `AGENTS.md`, `specs/`,
`docs/`, `src/`, `tests/`, `migrations/`, `.github/workflows/ci.yml` y el historial
Git local.

## Matriz de entregables

| Entregable | Evidencia concreta | Estado: Completo/Parcial/Falta | Acción pendiente |
|---|---|---|---|
| ODD: problema, usuarios y outcomes | `specs/outcomes.md` define visitante, celador y vigilancia; OUT-01 a OUT-05. Declara explícitamente que el problema es un supuesto académico. | Completo | Mantener la distinción entre outcome previsto y resultado medido en la exposición. |
| SDD: requisitos y reglas | `specs/requirements.md`, `business-rules.md` (BR-01 a BR-33) y `acceptance-criteria.md` (AC-B01 a AC-17). | Completo | Resolver las preguntas abiertas D-03 a D-06 solo si el equipo las presenta como decisiones formales. |
| SDD: arquitectura, stack y modelo | `specs/architecture.md`, `data-model.md`, `api.md`; código FastAPI, SQLAlchemy, Alembic, Jinja, JavaScript y SQLite/PostgreSQL previsto. | Parcial | Corregir los documentos que aún describen la base como si las historias no existieran; ejecutar PostgreSQL antes de afirmar soporte. |
| Plan y tareas | `specs/implementation-plan.md` y `tasks.md` enlazan BASE, HU-01 a HU-05, QA-01 y ENTREGA-01 con criterios. | Parcial | Ajustar estados textuales de tareas/issues al estado real de pruebas y revisión. |
| Reserva, consulta, cancelación y vencimiento | Servicios `reservations.py`, vistas y pruebas `test_reservations.py`; BR-01 a BR-06 y AC-01 a AC-04. La auditoría corrigió la creación de `Allocation` para reservas pendientes. | Parcial | Actualizar las pruebas HTTP a roles `admin/client` y payload con `customer_name`/`scheduled_at`; ejecutar la suite completa. |
| Prevención de doble reserva | `tests/integration/test_integration.py::test_last_preferential_reservation_race_single_winner`; ejecutada hoy: PASS. Dos hilos, un ganador y 20 asignaciones preferenciales. | Completo | Repetir contra PostgreSQL antes de declararlo multibase. |
| Ingreso reservado y espontáneo | `entries.py`, vistas de garita y `test_entries.py`; conversión reserva->estadía y walk-in general. | Parcial | Suite HTTP pendiente de actualización/ejecución; probar manualmente la ruta autenticada después del ajuste de sesión de esta auditoría. |
| Capacidad y asignación | `spaces` P001-P020/G001-G080, `allocations`, `allocation_guard`, `effective_availability`; integración de último general ejecutada hoy: PASS. | Parcial | Añadir/ejecutar prueba HTTP actualizada para visualizar capacidad con roles demo. |
| QR y tickets cerrados | QR en `reservations.py`/`entries.py`, ticket digest en `exits.py`, pruebas presentes para reuso de ticket cerrado. | Parcial | Las pruebas correspondientes existen pero no se ejecutaron completas hoy; validar el lector de cámara en Chrome/Edge durante el ensayo de demo. |
| Cobro y liberación | `exits.py`: 2 centavos/minuto, redondeo entero, pago idempotente y borrado de `Allocation`; AC-09 a AC-11 y pruebas presentes. | Parcial | Ejecutar `test_exits.py` actualizado y una prueba de UI autenticada. |
| Alerta >24h | `alerts.py`: solo `open`, comparación estricta `entered_at < now-24h`; AC-12 y pruebas presentes. | Parcial | Ejecutar `test_alerts.py` actualizado a roles `admin`. |
| Multa por discordancia QR/placa/espacio | CAMBIO-01: RF-11, BR-34 a BR-37, AC-18, migración `0006`, `exits.py` y prueba integrada ejecutada. Registra 2,500 centavos una sola vez. Recuperación por placa sigue excluida. | Parcial | Ejecutar la ruta HTTP/formulario autenticada y actualizar la suite HTTP heredada. |
| Migraciones y datos demo | Alembic `0001` a `0005`; `demo.py`; prueba `test_demo_seed_idempotent_and_scenarios` ejecutada hoy: PASS. | Parcial | Probar `alembic upgrade head` y demo sobre una BD descartable separada fuera de pytest; no usar la BD de usuarios. |
| Pruebas automatizadas y CI | 79 pruebas recolectadas; workflow `.github/workflows/ci.yml` instala, compila y ejecuta pytest. Hoy pasaron 3 pruebas de integración y compilación; no se consultó una ejecución remota. | Parcial | Arreglar pruebas HTTP desalineadas y ejecutar suite completa en SQLite y PostgreSQL; revisar CI remoto. |
| Registro de IA | `docs/ai-log.md` tiene columnas Actividad, Solicitud, Resultado real y Decisión. | Parcial | Añadir una entrada para esta auditoría y para cada decisión humana posterior; no convertir decisiones del agente en aprobación humana. |
| Colaboración y rotación | `docs/team-plan.md` define tres ciclos rotativos. Git conserva commits/merges de Jack García, Alex Jimenez y Francisco Herrera. Ocho commits de HU-01 a HU-03 llevan autor `Your New Name <your_email@example.com>`. | Parcial | Corregir identidad Git futura y registrar revisión/rotación realmente realizada; el plan de roles no prueba la participación histórica. |
| Git: ramas, commits, issues y PR | Historial local: PR merges #10, #11, #12, #13, #14; ramas `feature/hu-*`, `Parte-de-AJ`, `codex/*`. `docs/github-state.json` registra Project 4, issues #1-#9 y PR #10. | Parcial | Verificar en GitHub con una sesión autorizada los issues, Project y PR actuales; esta auditoría no hizo consulta remota. |
| Cambio de requisito | Migraciones `0002`-`0005`, BR-31 a BR-33, AC-15 a AC-17, API v0.3 y commit `7e7d1f2` documentan roles `admin/client`, programación manual, QR único y tablero. | Parcial | Conservar la solicitud original fechada y una revisión humana; no está archivada como artefacto independiente en el repositorio. |
| README y preparación | `README.md` contiene alcance, instalación, restricciones y enlaces. | Parcial | Actualizar sus afirmaciones históricas de “base” y sus credenciales/pasos demo sin exponer secretos. |

## Verificaciones ejecutadas hoy

Entorno observado: Windows, PowerShell, Python 3.14.3 en `.venv`, pytest 9.2.0,
SQLite temporal por fixture. `TEST_POSTGRES_URL` no estaba definido; por ello no
hubo prueba PostgreSQL. La aplicación y los datos de la demo no fueron modificados
para ejecutar estas pruebas.

| Comando | Resultado real |
|---|---|
| `python -m pytest --collect-only -q -p no:cacheprovider` | PASS: 79 pruebas recolectadas. |
| `python -m pytest tests/integration/test_integration.py -q --basetemp .tmp\\pytest-audit-integration -p no:cacheprovider` | PASS: 3 passed, 4 warnings, 2.12 s. Cubre último general, último preferencial y seed demo idempotente. |
| `python -m compileall -q src tests migrations scripts` | PASS: código compiló sin salida de error. |
| `python -m pip check` | PASS: “No broken requirements found.” |
| `python -m pytest -x -vv ...` antes de corregir | FAIL: la prueba de último preferencial reveló 0 `Allocation` para 20 reservas. La causa era que `create_reservation` no persistía la asignación. |
| Suite completa `pytest -q` | Sin resultado final en esta auditoría: la consola excedió su límite mientras corría pruebas HTTP. No se declara aprobada. |

Las advertencias observadas fueron la deprecación de `fastapi.testclient` sobre
`httpx` y la advertencia de Alembic sobre `path_separator`; no causaron fallos en
las tres pruebas de integración.

## Corrección incremental realizada durante la auditoría

1. `create_reservation` ahora persiste `Allocation` de la reserva pendiente.
2. `enter_with_reservation` sustituye de forma atómica esa asignación por la de
   la estadía; conserva compatibilidad con reservas antiguas que no tengan fila.
3. Las mutaciones de reserva/cancelación usan una sesión nueva de asignación tras
   la dependencia de autenticación, para no reutilizar una sesión ya leída.
4. La prueba de carrera cuenta asignaciones por `Space.category`, no por una
   suposición de prefijo.

Esta corrección está cubierta por la prueba integrada repetida hoy. La ruta HTTP
autenticada queda como validación pendiente, por lo cual la funcionalidad se marca
Parcial y no como aceptación final.

## Brechas detectadas

- Las pruebas HTTP de reservas, garita, salidas y alertas todavía usan payloads
  antiguos (por ejemplo solo `plate`) y roles eliminados (`celador`, `vigilancia`),
  mientras código y migración `0003` exigen `admin/client` y la reserva requiere
  nombre y fecha/hora. Su presencia no equivale a prueba actual válida.
- No hay evidencia actual de PostgreSQL, CI remoto, estado actual del Project ni
  revisión humana.
- El historial tiene identidad genérica en commits de HU-01 a HU-03. No es
  atribuible de forma fiable a Francisco aunque las ramas/merges sí lo mencionan.

## Pendientes priorizados antes de presentar

1. Actualizar y ejecutar las pruebas HTTP para roles `admin/client`, el payload
   actual y CAMBIO-01; obtener resultado completo SQLite.
2. Ejecutar la misma suite contra una PostgreSQL descartable terminada en `_test`
   y revisar la ejecución de CI.
3. Hacer un ensayo autenticado de reserva -> ingreso con mismo QR -> salida/pago;
   verificar rechazo de QR/ticket cerrado y cámara en Chrome/Edge.
4. Verificar manualmente en GitHub el Project, issues, PR #10-#14 y sus estados;
   registrar solo URLs/estados observados.
5. Adjuntar el cambio de requisito original fechado y registrar revisión humana.

