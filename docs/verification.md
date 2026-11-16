# Verificación real de la preparación

Fecha: 2026-11-15, America/Panama. No aceptación humana ni resultado funcional
del estacionamiento. Este informe distingue comprobación estática de ejecución.

| Comprobación | Resultado real |
|---|---|
| Editor | Ventana VS Code con proyecto Proyecto_2 observada; README enviado al editor |
| Fuentes | Proyecto 2 (3 pp) y Tema 9 (35 pp) extraídos/leídos; PDFs originales conservados |
| Sintaxis Python | `python -m compileall -q src tests migrations scripts`: completado sin errores |
| AST | 17 archivos Python analizados correctamente |
| Configuración | pyproject.toml parseado con tomllib; JSON backlog/estado parseados |
| Documentos | 19 documentos solicitados presentes; nueve cuerpos de issue con secciones completas |
| Reglas | BR-01–BR-30 presentes |
| Enlaces | Primera pasada detectó falta de este informe; creado; segunda pasada PASS, sin enlaces locales rotos |
| Seguridad básica | Smoke real: sales distintas, credencial correcta/incorrecta y hash malformado; tokens distintos/digest; reloj UTC: PASS |
| Plan de publicación | `python scripts/sync_github.py`: muestra nueve issues, sin cambios remotos |
| Instalación | venv falló durante ensurepip; pip target no pudo obtener FastAPI por red restringida |
| pytest | `python -m pytest`: No module named pytest; NO ejecutado |
| Servidor/migración | Sin ejecución real, faltan dependencias; no se afirma que hayan pasado |
| PostgreSQL | Configurado, NO probado; CI escrito, NO ejecutado en GitHub |
| GitHub CLI | repo/issues/Projects y script --publish fallaron por proxy 127.0.0.1:9; sin URLs creadas |
| Rama | git switch --orphan no pudo crear .git/HEAD.lock; git status sigue main sin commits |
| Integración alternativa | Conectada y lectura confirmada: Stelar0720, main con Initial commit 973432095fbd2ea9f40d9125b7cc35af9a2e1b6e, issues vacíos. Crear issue y rama devolvió 403; sin escrituras exitosas |
| Navegador autorizado, actualización posterior | Project 4 creado y verificado con cinco columnas en orden; issues #1–9 creados y agregados en Pendiente; rama base/plaza-reserva creada desde main |

El smoke de seguridad usó únicamente módulos standard-library security.py/clock.py,
sin imprimir contraseñas ni tokens. No cubre auth HTTP, BD ni los flujos futuros.
El workflow y las pruebas escritas necesitan ejecución tras instalar dependencias.
Antes de aprobación humana: ejecutar instalación limpia, pip check, migración/seed,
pytest en SQLite/PostgreSQL, revisar UI y registrar resultados y versiones resueltas.

Git Bash: se preparó scripts/publish-base.sh. El intento de comprobarlo con
`bash -n` dentro de esta sesión no pudo iniciar Bash: CreateFileMapping, Win32
error 5. No se presenta como script ejecutado ni como validación Bash aprobada.
La inspección remota posterior a la pausa confirmó commit e279839 con tests/;
la publicación del resto y PR sigue pendiente del script o navegador.
