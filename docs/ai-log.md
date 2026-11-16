# AI Development Log

Fecha: 2026-11-15, America/Panama. Herramienta: Codex en esta sesión, shell
PowerShell/Python, apply_patch, GitHub CLI, búsqueda web oficial y lector pypdf.
No se afirma modelo concreto no verificado, revisión humana ni actividades de compañeros.

| Actividad | Solicitud | Resultado real | Decisión / origen |
|---|---|---|---|
| Inspección local | Retomar repo conservando trabajo | origin correcto; main sin commits, dos PDF y carpetas con gitkeep; sin AGENTS previo encontrado en workspace | Agente: conservar fuentes y estructura |
| Apertura de editor | Abrir Visual Studio y trabajar local | code . ejecutado; ventana observada `DSaIA-Proyecto2.txt - Proyecto_2 - Visual Studio Code` | Usuario autorizó apertura; no se modificó configuración del editor |
| Extracción de fuentes | Leer ambos antes de editar | Proyecto 2: 3 pp; Tema 9: 35 pp. Python local falló por DLL; runtime PDF incluido pudo descifrar. pp 7/23: extracción de bloques BT/ET evita parsear dibujo vectorial masivo | Agente: usar runtime disponible; PDFs intactos |
| Consulta metodológica | Requisitos académicos y método | Lectura completa de texto; distinción ODD de Tema 9 y recorrido de outcomes de Proyecto 2 documentada | Requisitos fuente + solicitud del usuario; sin ejemplos copiados como reglas |
| Compatibilidad | No copiar dependencias antiguas | Metadatos oficiales FastAPI/SQLAlchemy/Alembic consultados; Python local 3.12.9 | Agente: familias/rangos provisionales, sin lock ni compatibilidad ejecutada inventada |
| Especificaciones | Preparar solo base y contratos | specs/ y docs/, criterios Dado/Cuando/Entonces, trazabilidad, propuestas y preguntas | Reglas BR-01–30 confirmadas por solicitud; D-03–06 propuestas del agente pendientes de revisión |
| Base | Esqueleto compartido | Código/config/modelos/migración/auth/layout/salud/seed y pruebas/workflow escritos | Agente: no implementar historias de Francisco/Alex ni ampliación |
| Instalación/verificación | Ejecutar controles apropiados | ensurepip de venv falló; pip target no pudo obtener fastapi por red; pytest ausente; compileall y controles estáticos registrados en verification.md | Agente: reportar pendiente ejecución, no declarar tests verdes |
| GitHub | Crear issues/Project/rama/PR autorizados | Consultas repo/issues/Project fallaron por proxy 127.0.0.1:9; intento de rama denegado por .git/HEAD.lock | Agente: preparar nueve cuerpos y script idempotente; no inventar URLs/commits/PR |
| Handoff | Miniprompts de compañeros | Documentos completos basados en módulos reales y contratos futuros claramente rotulados | Agente: exigir base integrada y coordinación; sin asignar cuentas desconocidas |
| Alternativa GitHub | Buscar vía conectada si CLI falla | Inicialmente disponible sin conectar; después aparecieron herramientas y se verificó cuenta Stelar0720/repositorio/main; búsqueda de issues vacía. Intentos de crear BASE-01 y rama devolvieron 403 | Agente: conservar commit inicial remoto 973432095fbd2ea9f40d9125b7cc35af9a2e1b6e; no afirmar escrituras exitosas |
| Publicación por navegador | Usuario abrió GitHub y pidió continuar | Sesión web permitió crear Project 4, columnas del flujo y issues #1–9, todos Pendiente; rama base/plaza-reserva desde main creada | Agente: conservar main, sin cierres ni aceptación humana; publicar archivos y PR a continuación |

## Confirmaciones humanas

Actualización de publicación: se verificó mediante GitHub que el commit
`e279839177e31a3b80b6276242d2ed5621475c90` contiene las pruebas de base; la última
carga del navegador sí terminó antes de la pausa. Se preparó
`scripts/publish-base.sh` para completar la subida desde Git Bash, conservando el
historial remoto y creando/reutilizando un PR borrador. Preparación del script
no significa que el usuario ya lo haya ejecutado.

El usuario proporcionó caso/reglas/reparto y autorizó archivos, backlog, rama y PR,
sin fusión ni despliegue. Indicó haber instalado pypdf. **No hay aceptación humana
de esta base, revisión de PR, ejecución por compañeros, feedback empresarial ni
cambio inesperado real registrado**. No completar esos hitos retroactivamente.

Para próximos incrementos agregar actividad/herramienta/solicitud/resultado/decisión,
con comandos/URLs/hashes reales cuando existan y aprobación humana identificada.

- 2026-11-15T17:13:35.757361-05:00: Publicación por script: https://github.com/Stelar0720/proyecto_2_topicos_II/pull/10. Rama base/plaza-reserva publicada desde su historial remoto; PR creado o reutilizado sin fusión. No equivale a ejecución de pruebas ni aceptación humana.

## HU-01 · Apoyo a Francisco (2026-11-16)

Herramienta: agente de codificación con shell Bash, GitHub CLI (`alosslessdev`),
pytest, PostgreSQL 17 en contenedor descartable, Chromium automatizado, `zbarimg`
y sondas HTTP propias. Solicitud del usuario (Francisco): revisar/implementar HU-01
partiendo de una base real en `main`, sin fusionar PR ni inventar revisiones.

| Actividad | Solicitud | Resultado real | Decisión / origen |
|---|---|---|---|
| Inspección inicial | Comprobar base integrada | `origin/main` solo con `README.md`; PR #10 en DRAFT | Agente: no crear rama de historia; limitar a revisión |
| Revisión BASE-02 | Revisar sin fusionar | `pytest` 24 passed con SQLite+PostgreSQL local; CI del PR verde; smoke uvicorn; sonda de bloqueo serializa en ambos motores | Agente: comentario de revisión en PR #10, sin aprobación |
| Integración | El usuario indicó que el PR estaba fusionado | Verificado: PR #10 MERGED, merge commit `2fc93de`, `2026-11-16T01:06:29Z` | **Confirmación humana (Francisco)**; no la ejecutó el agente |
| Defecto de base | Formulario HTML bloqueado | Sonda: `Referrer-Policy: no-referrer` ⇒ Chrome envía `Origin: null` en POST del mismo origen; `same_origin` respondía 403 | Agente: aceptar `Sec-Fetch-Site: same-origin`; requiere revisión de Jack por ser archivo compartido |
| HU-01 | Implementar T-01A/B/C | `reservations.py`, vistas, pruebas y commits `T-01A`/`T-01B`/`T-01C` | Agente: D-03/D-04 aplicadas como propuestas, marcadas pendientes |
| Verificación | Ejecutar pruebas reales | 33 passed SQLite; 62 passed con PostgreSQL 17; QR decodificado con `zbarimg`; vista ejercitada en Chromium | Agente: resultados de esta sesión, sin aceptación humana |
| Dependencias | No copiar de otros proyectos | Añadidas `segno 1.6.6` (QR SVG, sin dependencias) y `python-multipart 0.0.33` (formularios FastAPI) | Agente: justificar en PR; `pyproject.toml` es compartido |

No hay aprobación de Product/Spec para D-03/D-04, ni revisión del PR de HU-01, ni
validación con un negocio real. Las tareas T-01A–C quedan implementadas y probadas,
no "Terminadas".

## HU-02 · Consulta y cancelación privadas (2026-11-16)

| Actividad | Solicitud | Resultado real | Decisión / origen |
|---|---|---|---|
| HU-02 | Continuar con T-02A/B tras HU-01 | `lookup`/`cancel` en `reservations.py`, vistas `/mi-reserva`, pruebas privadas; commits T-02A y T-02B en rama apilada | Agente: base `feature/hu-01-reservas` porque el PR de HU-01 sigue en revisión; no se publica aún |
| Cancelación repetida | D-05 propuesta | Repetir devuelve el mismo estado terminal; usada → 409; vencida informa `expired` | Agente aplica la propuesta de `docs/decisions.md`; sin confirmación de Product/Spec |
| Verificación | Pruebas y vista reales | 44 passed SQLite y 84 con PostgreSQL 17; Chromium: consulta vigente, cancelación y estado terminal; disponibilidad vuelve a 20 | Agente: resultados de esta sesión |

## HU-03 · Ingreso con reserva y espontáneo (2026-11-16)

| Actividad | Solicitud | Resultado real | Decisión / origen |
|---|---|---|---|
| Integración | Usuario pidió continuar con la cadena | PR #11 fusionado con `--merge` (`daeed78`), autorizado con "hazlo"; rama de HU-02 rebasada y PR #12 abierto | **Instrucción humana**; el agente ejecutó el merge pedido |
| HU-03 | Implementar T-03A/B | `entries.py`, `templates/entries/`, `static/entries.js`, pruebas; commits T-03A y T-03B | Agente: `require_roles` para API y páginas propias 401/403 en vistas |
| Sesión nueva | Asignación con personal autenticado | `allocation_transaction` rechazó la sesión de la petición porque ya leyó la sesión del personal; se abre sesión nueva para la asignación | Agente: mantiene la regla del handoff; probado en pruebas |
| Verificación | Pruebas y navegador | 60 passed SQLite, 116 con PostgreSQL 17; Chromium: ingreso espontáneo G001 con QR decodificado por `zbarimg`, ingreso con reserva en P001, placa duplicada rechazada | Agente: resultados de esta sesión |

## Cierre documental (2026-11-16)

| Actividad | Solicitud | Resultado real | Decisión / origen |
|---|---|---|---|
| Contrato | Documentar lo implementado | `specs/api.md` v0.2: campos aditivos y regla `Origin`/`Sec-Fetch-Site` | Agente: sin cambiar rutas ni códigos ya usados |
| Rollback | Probar fallo a mitad de conversión | Prueba nueva con fallo forzado tras las escrituras: nada persiste y el segundo intento entra | Agente: `17 tests` de entradas en SQLite |
| Tablero | Revisar por qué sigue Pendiente | Falta scope de proyectos en el token; se documentan los pasos exactos sin inventar IDs | Agente: no se modificó el tablero |

## HU-04/HU-05/QA-01 - Apoyo de Alex (2026-11-16, rama \Parte-de-AJ\)

Herramienta: agente de codificacion (opencode), shell PowerShell/Python, venv local, pytest.
Solicitud del usuario: implementar HU-04 T-04A/B, HU-05 T-05A y QA-01 T-QA1/2 en \Parte-de-AJ\, subir avances.

| Actividad | Solicitud | Resultado real | Decision / origen |
|---|---|---|---|
| Rama y base | Trabajar en rama acordada | \origin/Parte-de-AJ\ rastreada localmente desde \cb4fa13\ (HU-03 integrado en main) | Usuario indico rama \Parte-de-AJ\; commits publicados alli |
| HU-04 T-04A/B | Salida/cotizacion/cierre idempotente | \exits.py\, \	emplates/exits/*\, pruebas en \	ests/test_exits.py\, rutas registradas en \main.py\, enlace en \ase.html\ | Calculo entero us (2c/min, fraccion arriba, D-06); cierre en sesion nueva + \llocation_transaction\, 1 pago, libera allocation; idempotencia por \Idempotency-Key\ |
| HU-05 T-05A | Alerta >24h | \lerts.py\, \	emplates/alerts/*\, vista \/vigilancia\, \	ests/test_alerts.py\ | Estrictamente >24h, solo abiertas, informativa, roles vigilancia/celador/admin |
| QA-01 T-QA1/2 | Demo e integracion | `demo.py`, CLI \seed-demo\ (BD separada, ref 2026-11-15T17:00:00Z, 6 escenarios, idempotente), \	ests/integration/test_integration.py\ | Integra carreras de reserva/ingreso/cierre; no borra datos ajenos; namespace demo |
| Correcciones | Entorno/pruebas | Ajuste `cli.py` (mojibake que rompia import/coleccion) y flush en `demo.py` para FK; fix nav \ase.html\ | Necesario para ejecutar suite |
| Verificacion | Ejecutar pruebas | `compileall -q src tests` OK; `pytest -q` (SQLite, sin `TEST_POSTGRES_URL`) **79 passed, 77 warnings, 47.04s** | PostgreSQL real no ejecutado por falta de `TEST_POSTGRES_URL` |
| Documentacion | Actualizar contratos/traza | `specs/api.md`, `docs/traceability.md`, `docs/ai-log.md` actualizados con resultados reales | Sin inventar PR/revision/aprobacion |

No hay PR creado/fusionado, ni issues/tablero actualizados, ni CI remoto verificado, ni aceptacion humana.
