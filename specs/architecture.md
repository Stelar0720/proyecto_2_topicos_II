# Arquitectura propuesta y fundamento compartido

Una aplicación FastAPI síncrona sirve HTML Jinja, CSS y JavaScript simple y API
del mismo origen. Routers → servicios por historia → SQLAlchemy → SQLite/PostgreSQL.
Alembic es la única vía de modificar esquema. Sin microservicios ni segundo framework.
La libertad tecnológica del Proyecto 2 se concreta en esta propuesta del equipo.

Python objetivo: 3.12. Dependencias con límites de versiones en `pyproject.toml`,
consultadas contra metadatos oficiales el 2026-11-15; ver `docs/decisions.md`.
No se ha generado un lock resuelto ni se afirma compatibilidad ejecutada donde
no hay pruebas reales. Las dependencias transitivas FastAPI/Starlette/Pydantic
las resuelve pip; no fijar Starlette por separado sin comprobar FastAPI.

## Componentes reales de la base

`config.py`: entorno; `db.py`: engine, sesiones, FK SQLite y transacción de
asignación; `models.py`: contrato compartido; `clock.py`: reloj UTC inyectable;
`security.py`: PBKDF2 y tokens; `auth.py`: sesiones del personal; `main.py`:
salud, errores, vistas y composición; `cli.py`: espacios y alta local de personal.
No hay servicios de reservas/ingresos/salidas todavía.

## Concurrencia para las próximas historias

La fila única `allocation_guard(id=1)` serializa las escrituras de asignación,
incluyendo creación/cancelación/vencimiento/conversión/cierre. Para 100 espacios
es una propuesta deliberadamente simple. Todas esas rutas deben usar
`allocation_transaction(session)` con una sesión nueva, sin lecturas previas.

- PostgreSQL: transacción + `SELECT ... FOR UPDATE` sobre la fila guardia.
- SQLite: `BEGIN IMMEDIATE`, que toma el bloqueo de escritura antes de leer.
  `FOR UPDATE` no protege en SQLite; no usarlo como sustituto. FK activadas por conexión.
- Dentro del bloqueo: capturar reloj, liberar reservas vencidas, validar placa,
  seleccionar espacio, escribir reserva/estadía/asignación/pago y hacer un solo commit.
  Cualquier fallo revierte todo. Los UNIQUE de `allocations.space_id` y `plate`
  son la segunda defensa de BD, junto con índices de reserva pendiente y estadía abierta.
- Esperas agotadas: 503 `DATABASE_BUSY`, cliente reintenta con la misma clave;
  conflictos de integridad: 409 tipado, después de rollback. Nunca éxito ficticio.

Los índices no pueden expresar el paso del tiempo: una reserva vencida se ignora
en lectura y se normaliza dentro del bloqueo antes de reusar una placa/espacio.
No hay scheduler obligatorio. Las carreras reales de las historias deben probarse
con conexiones independientes y barreras en ambos motores; no con SQLite en memoria.

## Seguridad

Alta de personal exclusivamente CLI con `getpass`, sin registro público.
PBKDF2-HMAC-SHA256 con sal aleatoria; sesiones aleatorias, solo digest persistido,
cookie HttpOnly/SameSite=Strict y Secure en producción. Caducidad comprobada en
servidor; baja de usuario invalida acceso. Mutaciones exigen Origin del mismo origen.
Login limitado por proceso; un limitador compartido y TLS son requisitos previos a
publicación con múltiples workers. No registrar cuerpos, cookies ni códigos.

QR visitante/estadía futuros: token aleatorio de 32 bytes, almacenar SHA-256, QR
sin placa ni nombre. Consulta privada por POST con código en cuerpo, no URL de API.
Propuesta para entrega QR: fragmento de URL leído por JS, sin enviarlo al servidor
ni analítica; no cargar recursos externos. Código manual usa el mismo secreto.

## Coordinación

Jack: modelos, migraciones, configuración, dependencias, auth, composición y layout.
Alex: workflow CI coordinado con Jack. Francisco/Alex agregan módulos por historia
según handoff. No modificar la migración 0001 una vez integrada: crear sucesora,
coordinar revisión única de heads y probar upgrade/downgrade en base descartable.
PostgreSQL configurado, **no declarado probado hasta ejecución real**.
