# Contratos API v0.1

JSON, rutas `/api`, timestamps ISO 8601 UTC con offset, dinero como `amount_cents`.
Errores: `{"error":{"code":"...","message":"..."}}`. Validación 422 sin
reflejar inputs sensibles. 401 `AUTH_REQUIRED`/`INVALID_CREDENTIALS`, 403
`FORBIDDEN`/`ORIGIN_REQUIRED`, 404 `NOT_FOUND`, 409 conflictos, 429 `RATE_LIMITED`,
503 `DATABASE_UNAVAILABLE`/`DATABASE_BUSY`. No exponer SQL, códigos ni datos ajenos.

## Implementado en el esqueleto (pendiente de ejecución donde se indique)

| Método / ruta | Entrada | Salida / acceso |
|---|---|---|
| GET `/health` | — | 200 `{status:"ok",database:"ok"}` con SELECT 1; 503 si BD inaccesible |
| GET `/` | — | HTML público, base pendiente sin operaciones de parking |
| GET `/acceso` | — | HTML login de personal |
| GET `/personal` | cookie | HTML protegido; módulos pendientes |
| POST `/api/auth/login` | `{username,password}` + Origin | 200 usuario, Set-Cookie `plaza_session`; 401/422/429 |
| GET `/api/auth/me` | cookie | 200 `{id,username,role}` o 401 |
| POST `/api/auth/logout` | cookie + Origin | 204, revoca sesión y cookie; repetición 204 |

## Contratos propuestos para historias futuras: NO existen todavía

| Historia | Método / ruta | Cuerpo / respuesta prevista |
|---|---|---|
| HU-01 | GET `/api/availability` | `{as_of,preferential:{available,total:20},general:{available,total:80}}`; sin placas |
| HU-01 | POST `/api/reservations` | `{plate}` → 201 `{status,space_code,created_at,expires_at,private_code}`; QR generado en UI con el código, mostrado solo al crear |
| HU-02 | POST `/api/reservations/lookup` | `{private_code}` → estado efectivo, placa propia, espacio, timestamps |
| HU-02 | POST `/api/reservations/cancel` | `{private_code}` → estado terminal; no revelar existencia con credencial inválida |
| HU-03 | POST `/api/entries/reservation` | personal celador/admin, `{private_code,plate}` → 201 estadía, ticket privado |
| HU-03 | POST `/api/entries/walk-in` | personal celador/admin, `{plate}` → 201 estadía, ticket privado e impresión |
| HU-04 | POST `/api/exits/quote` | celador/admin, `{ticket_code}` → estado/importe provisional/as_of; no muta |
| HU-04 | POST `/api/exits/close` | celador/admin, `{ticket_code,payment_confirmed:true}` + `Idempotency-Key` → 200 cierre con importe calculado en servidor a `exited_at` |
| HU-05 | GET `/api/alerts/long-stays` | vigilancia/celador/admin → placa, espacio, entered_at, elapsed_seconds, as_of |

Conflictos: `CATEGORY_FULL`, `PLATE_BUSY`, `RESERVATION_EXPIRED`,
`RESERVATION_CANCELLED`, `RESERVATION_USED`, `PLATE_MISMATCH`, `STAY_CLOSED`,
`IDEMPOTENCY_CONFLICT`. Código privado inválido → 404 genérico, sin distinguir
credencial inexistente de ajena. Nada de listado público de reservas ni búsqueda por placa.

Idempotencia de cierre: misma clave + mismo ticket devuelve cierre original;
misma clave + otro ticket → 409; otro reintento del ticket ya cerrado devuelve
su cierre original, sin pago ni salida nuevos. El importe definitivo se calcula
al confirmar, no se acepta cantidad del navegador. QR cerrado jamás autoriza otro vehículo.
Ingreso repetido con reserva usada → 409, no nueva estadía.

Vistas futuras propuestas: `/reservar`, `/mi-reserva`, `/garita`, `/salidas`,
`/vigilancia`; deberán añadirse con su historia. No son enlaces funcionales de la base.
Revisar contratos con Jack antes de implementar; no considerar un contrato aprobación humana.
