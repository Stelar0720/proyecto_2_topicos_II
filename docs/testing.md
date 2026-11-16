# Verificación de la base

## Ejecución prevista desde la raíz

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests migrations scripts
.\.venv\Scripts\python.exe -m pytest
```

Las fixtures migran una SQLite de archivo temporal por prueba. Con
`TEST_POSTGRES_URL` también ejecutan cada prueba de BD contra PostgreSQL en un
schema aleatorio aislado, creado/borrado por fixture. La BD debe terminar en `_test`
y ser descartable; nunca usar una BD de producción. La contraseña de Actions
es solo para el servicio efímero de CI, no para personal ni publicación.

Pruebas escritas: AC-B01–B06; sesión/caducidad/logout, privacidad de errores,
sal/password/token, idempotencia del seed, migración/modelos/downgrade,
rollback y restricciones de placa/asignación. No confundir estas restricciones
con pruebas de flujos o carreras que todavía no existen.

## Evidencia local real (2026-11-15)

- Python instalado: 3.12.9. Fuentes extraídas: Proyecto 2, 3 páginas; Tema 9, 35 páginas.
- El Python instalado por el usuario no pudo cargar `_cffi_backend` (Access denied).
  Se usó el runtime PDF incluido en Codex; páginas 7/23 contienen mucho dibujo
  vectorial y se extrajeron sus bloques de texto por separado. Originales intactos.
- `python -m venv .venv`: falló durante ensurepip; puede quedar un entorno parcial ignorado por Git.
- Instalación de dependencias: no completada por restricciones de red de la sesión.
- pytest/arranque/upgrade real SQLite/PostgreSQL: **pendientes de ejecución**.
- CI: workflow preparado con PostgreSQL 17; sin ejecución remota verificada.
- Resultados estáticos y validaciones adicionales: `verification.md` (generado al cierre).

## Plan de pruebas funcionales por autor

Francisco: dos solicitudes simultáneas/último preferencial o general, liberación al
vencer exactamente, conversión atómica con rollback, placa duplicada, QR reserva
reutilizado, código manual, cancelación privada, accesos no autorizados. Conexiones
independientes, barreras y SQLite de archivo + PostgreSQL real; no simular carrera con mocks.

Alex: reloj fijo, redondeo exacto por microsegundos y centavos, pago/cierre reintentado
con misma/distinta clave, QR cerrado frente a otro vehículo, alerta 24h−1µs/24h/24h+1µs,
roles, demo y pruebas de integración. Cada autor conserva sus pruebas; Alex coordina
la integración sin convertirse en QA único de todo el equipo.

## Datos demo futuros (QA-01, Alex)

Referencia común propuesta `2026-11-15T17:00:00Z` (12:00 Panama), reloj FrozenClock
y base `data/plaza_demo.db` separada, nunca apuntar por defecto a datos de usuarios.
El comando `seed-demo` **no existe todavía**.

| Escenario | Placa única | Espacio | Instantes relativos a referencia |
|---|---|---|---|
| Reserva vigente | DEMO01 | P001 | creada −5min, vence +25min |
| Reserva vencida | DEMO02 | P002 | creada −40min, venció −10min; sin asignación activa |
| Estadía abierta | DEMO03 | G001 | entrada −10min |
| Estadía >24h | DEMO04 | G002 | entrada −25h |
| Estadía cobro | DEMO05 | G003 | entrada −65min |
| Estadía cerrada/pagada | DEMO06 | G004 | entrada −120min, cierre/pago −60min; sin asignación activa |

Usar IDs estables del namespace demo y verificarlos antes de insertar. Segunda carga
no duplica ni borra; si hay colisión con datos ajenos, abortar sin cambios. No crear
recargos. QR/códigos de demostración se entregan por canal local, no en logs de aplicación.
