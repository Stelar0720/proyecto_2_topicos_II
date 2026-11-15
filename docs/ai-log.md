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
