# Plaza Reserva

**Base inicial académica; no es una aplicación terminada.** Proyecto 2 de Tópicos
Especiales II, equipo Jack, Francisco y Alex. Caso y metas son supuestos académicos,
sin entrevistas, aprobación empresarial ni resultados medidos de un negocio real.

El control manual dificulta distinguir espacios disponibles, reservados y ocupados
y registrar ingresos, salidas y cobros consistentemente. Se propone una web para
reservar o ingresar según cupo, evitar duplicados y mantener estadías y pagos coherentes.

## Alcance

Plaza ficticia: 20 preferenciales P001–P020 para reservas programadas de 30 minutos y
80 generales G001–G080 para espontáneos. Operación continua, America/Panama y B/.
El administrador coteja placa/acceso físico manualmente. La tarifa es B/.0.02 por
minuto, redondeando cada fracción hacia arriba desde el ingreso real; hay alerta
informativa al superar 24 horas.

La demo incluye reservas con nombre y calendario, consulta/cancelación, ingreso,
un único QR por visita (entrada y salida), ticket, cobro manual, alertas y tablero
administrativo. Solo existen los roles `admin` y `client`.

Sin sensores, barreras ni pasarela. El escáner QR usa la cámara del navegador cuando
está disponible y siempre mantiene entrada manual como alternativa.
CAMBIO-01 coteja QR, placa y espacio en la salida: si placa o espacio declarado
no coincide con la estadía, se registra una multa única de B/.25.00 junto al pago.
Incidencias y recuperación por placa continúan fuera de alcance. ALPR: fase 2.

## Fuentes y método

[Proyecto 2](DSaIA-Proyecto2.pdf) gobierna requisitos académicos;
[Tema 9](DSaIA-Tema9.pdf) complementa especificaciones vivas, criterios, tareas
pequeñas, historias completas y trazabilidad. Se leyeron ambos el 2026-11-15.
Tema 9 usa ODD como **Organic Driven Development**; aquí seguimos primero el
problema y los outcomes del usuario exigidos por Proyecto 2, después SDD.

## Tecnología y estructura

Python 3.12, FastAPI, SQLAlchemy, Alembic, Jinja/HTML/CSS/JavaScript simple,
pytest y GitHub Actions. SQLite local, PostgreSQL previsto para publicación.
Metadatos y límites de versión: [decisiones](docs/decisions.md).

```text
src/plaza_reserva/     configuración, BD, modelos, auth, salud y vistas comunes
migrations/           migración 0001 y entorno Alembic
tests/                pruebas de base y fixtures de reloj/motores
specs/                outcomes, contratos, criterios, plan y tareas
docs/handoff/         miniprompts de Francisco y Alex
docs/issues/          nueve cuerpos de issues listos para publicar
scripts/              sincronización reintentable del backlog con gh
.github/workflows/    CI previsto con SQLite y PostgreSQL
```

## Instalación y ejecución del esqueleto

Desde esta carpeta, en PowerShell con Python 3.12 y acceso a PyPI:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m plaza_reserva.cli seed-spaces
.\.venv\Scripts\python.exe -m plaza_reserva.cli create-staff --username admin --role admin
.\.venv\Scripts\python.exe -m uvicorn plaza_reserva.main:create_app --factory --reload --no-access-log
```

Si ya tienes `.env`, consérvalo: no vuelvas a copiarlo encima. La contraseña se
solicita oculta por CLI, no se incluye en argumentos ni tiene valor predeterminado.
Abrir `http://127.0.0.1:8000`, acceso en `/acceso`, área protegida `/personal`,
salud `/health`. No necesitas activar el entorno ni cambiar políticas de PowerShell.

Para PostgreSQL configura `DATABASE_URL=postgresql+psycopg://...` en `.env` y
ejecuta la misma migración/seed. No creamos ni contratamos un servidor aquí.
Producción requiere `APP_ENV=production`, `COOKIE_SECURE=true`, hosts explícitos y
PostgreSQL; TLS/limitador compartido y despliegue siguen pendientes.

## Pruebas y estado de verificación

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests migrations scripts
.\.venv\Scripts\python.exe -m pytest
```

Para incluir PostgreSQL, definir `TEST_POSTGRES_URL` a una BD descartable cuyo
nombre termine `_test`. Se usan schemas aislados por prueba, creados/eliminados
por fixture. No apuntar a una BD real de usuarios. Instrucciones y matriz:
[testing](docs/testing.md), [verificación real](docs/verification.md).

La sesión de preparación pasó comprobaciones estáticas, pero **no pudo instalar
dependencias ni ejecutar pytest/servidor/migraciones por restricciones del entorno**.
PostgreSQL está configurado, no probado. El workflow existe; no se afirma CI verde.
Los rangos aún no son un lock resuelto. No usar esta base como entrega funcional final.

## GitHub, incorporación y próximos pasos

[Repositorio](https://github.com/Stelar0720/proyecto_2_topicos_II).
**Project e issues publicados por navegador.**
[Tablero Plaza Reserva](https://github.com/users/Stelar0720/projects/4):
Pendiente → Listo → En desarrollo → En revisión → Terminado.
Los nueve issues están en Pendiente; no se afirma aceptación humana.
La rama remota `base/plaza-reserva` se creó desde el commit inicial de main.
La publicación de archivos y PR se registra al completarse en github-state.json.
El CLI local sigue restringido para red y escritura en .git; la integración
API dio 403 para escribir, pero la sesión de navegador autorizada sí permitió hacerlo.
Registro de URLs verificadas: [github-state.json](docs/github-state.json).
Pasos precisos y reintento sin duplicados: [GitHub setup](docs/github-project-setup.md).
Issues: [BASE-01 #1](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/1),
[BASE-02 #2](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/2),
[HU-01 #3](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/3),
[HU-02 #4](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/4),
[HU-03 #5](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/5),
[HU-04 #6](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/6),
[HU-05 #7](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/7),
[QA-01 #8](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/8),
[ENTREGA-01 #9](https://github.com/Stelar0720/proyecto_2_topicos_II/issues/9).

1. Jack verifica/publica y coordina revisión/integración de BASE-01/02 en main.
2. Francisco parte del commit integrado de base: HU-01 → HU-02 → HU-03.
3. Alex revisa criterios/CI y, tras HU-03 integrado, implementa HU-04/05 y QA-01.
4. Publicación/demo posterior coordinada por Jack y Alex; no desplegada en este paso.

Miniprompts completos: [Francisco](docs/handoff/francisco.md) y
[Alex](docs/handoff/alex.md). No reconstruir la base ni recrear tablero.
Responsables, rotación y coordinación: [team-plan](docs/team-plan.md).
Preguntas antes de historias/publicación: [decisiones](docs/decisions.md).
Tareas: [tasks](specs/tasks.md). Registro IA: [ai-log](docs/ai-log.md).

PR inicial (sin fusionar): [base compartida](https://github.com/Stelar0720/proyecto_2_topicos_II/pull/10).
