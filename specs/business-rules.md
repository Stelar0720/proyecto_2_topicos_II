# Reglas acordadas y estados

Los IDs BR-01–BR-30 conservan la numeración acordada por el equipo en la solicitud.

| ID | Regla |
|---|---|
| BR-01 | Para la demo, una reserva puede programarse en fecha/hora pasada o futura. |
| BR-02 | Retiene un preferencial durante 30 minutos desde la fecha/hora programada. |
| BR-03 | Al vencer sin ingreso deja de retenerlo: `now >= expires_at`. |
| BR-04 | Entregar QR y código privado para consultar/cancelar. |
| BR-05 | Celador verifica placa y confirma ingreso. |
| BR-06 | Reserva vencida, cancelada o utilizada no admite ingreso. |
| BR-07 | Espontáneo nunca recibe preferencial automáticamente. |
| BR-08 | Celador registra placa y asigna general disponible. |
| BR-09 | Ticket QR imprimible desde navegador. |
| BR-10 | Categoría llena: rechazar sin registros parciales. |
| BR-11 | Placa no tiene múltiples reservas pendientes ni múltiples estadías abiertas. |
| BR-12 | Conversión reserva vigente → estadía es atómica. |
| BR-13 | Espacio no se asigna simultáneamente a dos vehículos. |
| BR-14 | Concurrencia protegida en servidor y base de datos. |
| BR-15 | QR usa identificador privado impredecible, sin datos personales. |
| BR-16 | Código manual alternativo al lector. |
| BR-17 | QR de estadía cerrada no cierra otra salida. |
| BR-18 | Sin hora de salida contratada. |
| BR-19 | Tarifa de 2 centavos/minuto desde entrada real. |
| BR-20 | Fracción de minuto se redondea hacia arriba. |
| BR-21 | Cálculo monetario con enteros en centavos. |
| BR-22 | Celador registra pago manual y confirma salida. |
| BR-23 | Cierre libera espacio; reintentos no duplican pagos. |
| BR-24 | Alerta de estadía abierta cuando duración > 24 horas. |
| BR-25 | Exactamente 24 horas no activa alerta. |
| BR-26 | Alerta muestra placa, espacio y tiempo transcurrido. |
| BR-27 | Alerta informativa, sin recargo ni liberación. |
| BR-28 | Cliente y administración están autenticados; administración también opera la garita. |
| BR-29 | Visitantes sin enumeración de reservas ni datos ajenos. |
| BR-30 | No guardar secretos/códigos privados completos en logs. |
| BR-31 | Un mismo código QR identifica una visita: para una reserva se reutiliza al ingresar y al salir; un espontáneo recibe ese código al ingresar. |
| BR-32 | Dashboard: gris disponible, verde reservado u ocupado normal, rojo estadía abierta de más de 24 horas. |

## Estados y transiciones (contrato para historias futuras)

- Reserva: `pending` → `cancelled` (cancelación privada antes de vencer),
  `pending` → `expired` (`now >= expires_at`), `pending` → `used` (ingreso válido).
  Los tres destinos son terminales. Una reserva pendiente persistida pero vencida
  se interpreta como `expired` en cualquier lectura y jamás autoriza ingreso.
- Estadía: `open` → `closed` solo con pago manual registrado en la misma transacción.
  `closed` es terminal; reintento devuelve el mismo resultado del cierre original.
- Espacio (estado **derivado**, no columna mutable): `available` → `reserved`
  al reservar; `reserved` → `occupied` al ingresar; `reserved` → `available`
  al cancelar/vencer; `available` → `occupied` al ingreso espontáneo general;
  `occupied` → `available` al cerrar. No hay transición por alerta.

La disponibilidad para un instante calcula reservas `pending` cuya ventana cumple
`scheduled_at <= now < expires_at` y estadías `open`, sin depender de cron. Antes
de cualquier asignación, la transacción
normaliza reservas vencidas y elimina sus asignaciones. Esa limpieza es parte
obligatoria de HU-01/HU-03; no está implementada en la base.

## Propuestas técnicas que requieren revisión del equipo

- D-03: rechazar también una reserva cuando la placa ya tiene estadía abierta
  (`PLATE_BUSY`). Es una restricción conservadora adicional a BR-11.
- D-04: placas de 2–12 caracteres alfanuméricos o guion, mayúsculas y sin espacios
  exteriores; no eliminar guiones ni espacios interiores silenciosamente.
- D-05: cancelación repetida devuelve el mismo estado terminal; si ya está usada,
  responde 409. No modificar estados terminales.

Instantes: `created_at`, `expires_at=created_at+30min`, `cancelled_at`, `used_at`,
`entered_at`, `exited_at`, `paid_at`, todos UTC conscientes de zona. Capturar
`now` una vez por operación mediante `Clock.now()`; presentar en America/Panama.
Cobro futuro: `ceil(duración_microsegundos / 60_000_000) * 2`; a duración cero,
0 centavos (propuesta D-06). Rechazar reloj anterior a entrada; nunca flotantes.
