# Decisiones y preguntas

Fecha de preparación: 2026-11-15. Acuerdo significa instrucción explícita del usuario,
no revisión humana de los documentos ni validación por un negocio real.

| ID | Tipo / estado | Decisión y motivo |
|---|---|---|
| D-01 | Acordada | Plaza ficticia, 100 espacios, reglas BR-01–30, operación manual, alcance limitado a base. |
| D-02 | Propuesta técnica aplicada a base | Monolito FastAPI síncrono, SQLAlchemy, Alembic, HTML/Jinja/CSS/JS. |
| D-03 | Propuesta pendiente de revisión | Una placa tampoco reserva mientras tiene estadía abierta, coherente con UNIQUE de asignación. |
| D-04 | Propuesta pendiente antes HU-01 | Normalizar placa a mayúsculas, trim exterior, patrón `[A-Z0-9-]{2,12}`. Definir formatos extranjeros/excepciones si hiciera falta. |
| D-05 | Propuesta pendiente antes HU-02 | Cancelación repetida idempotente; utilizada → conflicto; vencida conserva estado efectivo vencido. |
| D-06 | Propuesta pendiente antes HU-04 | A cero tiempo, cero centavos; sin tarifa mínima no acordada. |
| D-07 | Propuesta técnica aplicada a esquema | Una fila guardia serializa asignaciones; SQLite BEGIN IMMEDIATE, PostgreSQL bloqueo de fila. UNIQUE/FK como segunda defensa. |
| D-08 | Propuesta técnica aplicada a base | PBKDF2, alta CLI, sesiones digest en BD, cookie privada; Origin mismo origen. Sin secretos predeterminados. |
| D-09 | Limitación verificada | PostgreSQL configurado pero no probado localmente. CI escrito, no ejecutado en GitHub todavía. |
| D-10 | Propuesta técnica | Rangos de dependencia, no lock inventado; congelar resolución solo tras instalar y pasar pruebas. |
| D-11 | Acordada | Ampliación futura de recargos/incidencias y recuperación; cambio concreto y evidencia real pendientes. ALPR fase 2. |

## Compatibilidad consultada antes de seleccionar rangos

Python local 3.12.9. Los metadatos oficiales actuales de [FastAPI](https://pypi.org/project/fastapi/)
y [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) admiten Python 3.12;
[Alembic](https://pypi.org/project/alembic/) declara SQLAlchemy >=2.0 y Python >=3.10.
Se eligieron las familias actuales indicadas en pyproject, sin copiar dependencias de otro proyecto.
FastAPI recomienda fijar una versión verificada y permitir que gestione Starlette:
[guía de versiones](https://fastapi.tiangolo.com/deployment/versions/).
Es una comprobación documental, **no prueba de resolución/ejecución**. Falta instalar,
`pip check`, pytest y registrar versiones resueltas antes de fijar un lock reproducible.

## Preguntas que bloquean historias o publicación, no la preparación de la base

- Q-01: revisar D-03/D-04 antes HU-01 y D-05 antes HU-02; responsable Product/Spec del ciclo.
- Q-02: confirmar D-06 antes HU-04 y criterio de cotejo manual de placa en HU-03.
- Q-03: usuarios GitHub verificados de Francisco/Alex. Issues sin assignee hasta conocerlos.
- Q-04: conservación/borrado de placas, responsables de cuentas y recuperación de acceso antes de publicar.
- Q-05: hosting, dominio, HTTPS y limitador compartido antes de despliegue; no contratar ahora.
- Q-06: asignar revisores humanos y obtener integración real de BASE-02 en main.
- Q-07: acceso operativo a red/Git de la sesión para publicar issues/Project/rama/PR; ver setup.

Actualización de Q-07: la integración GitHub ya conectada confirma lectura y el
commit inicial remoto; issue/rama rechazados con 403. No se necesita recrear el
repositorio ni sustituir main. La publicación sigue pendiente, no aceptada.
