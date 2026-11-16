# Modelo compartido inicial

El esquema prepara contratos; no implementa los flujos. Tipos UTC manejados por
`UTCDateTime`: TIMESTAMP con zona en PostgreSQL; UTC sin zona física en SQLite,
restaurado a consciente al leer. UUID textuales como IDs internos, nunca como
credencial pública por sí solos. Sin datos de tarjeta ni nombres de visitantes.

| Tabla | Campos principales / restricciones |
|---|---|
| spaces | code PK, category `preferential/general`; 100 códigos mediante seed |
| allocation_guard | id PK restringido a 1; fila creada en migración |
| staff | id UUID, username UNIQUE, password_hash, role `admin/client`, active, created_at |
| staff_sessions | token_hash PK, staff_id FK, created_at, expires_at |
| reservations | id, plate, space_id FK, status, token_hash UNIQUE, created_at, expires_at, cancelled_at, used_at |
| stays | id, plate, space_id FK, reservation_id FK UNIQUE opcional, ticket_hash UNIQUE, status, entered_at, exited_at |
| allocations | space_id PK, plate UNIQUE, reservation_id UNIQUE o stay_id UNIQUE (XOR); FK compuestas aseguran placa/espacio coincidentes |
| payments | id, stay_id FK UNIQUE, amount_cents entero >=0, mismatch_fee_cents entero >=0, paid_at, staff_id FK, idempotency_key UNIQUE |

Índices únicos parciales: reservation.plate donde `status='pending'` y stay.plate /
space_id donde `status='open'`. Reserva/estadía tienen UNIQUE(id,space_id,plate)
para FKs compuestas de allocations. Checks de status y timestamps terminales.
No guardar `available` en spaces: deriva de reservas vigentes/estadías abiertas.

La fila allocations es la asignación exclusiva compartida entre reserva y estadía.
La conversión sustituye la referencia a reserva por estadía en una transacción.
La BD evita dos filas para el mismo espacio/placa; el servicio debe validar estado,
categoría, expiración y la referencia de reserva. No introducir APIs que escriban
saltándose el bloqueo global. La base no ofrece esas APIs aún.

La multa CAMBIO-01 no crea un modelo de incidencias: se conserva como
`mismatch_fee_cents` en el único pago idempotente de la estadía. No se crean
recargos por otros motivos ni recuperación por placa.
