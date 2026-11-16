# Contratos API v0.2

JSON, rutas `/api`, timestamps ISO 8601 UTC con offset, dinero como `amount_cents`.
Errores: `{"error":{"code":"...","message":"..."}}`. Validación 422 sin
reflejar inputs sensibles. 401 `AUTH_REQUIRED`/`INVALID_CREDENTIALS`, 403
`FORBIDDEN`/`ORIGIN_REQUIRED`, 404 `NOT_FOUND`, 409 conflictos, 429 `RATE_LIMITED`,
503 `DATABASE_UNAVAILABLE`/`DATABASE_BUSY`. No exponer SQL, códigos ni datos ajenos.

v0.2 documenta lo que las historias implementaron. Los campos añadidos respecto a
v0.1 (`plate`, `status_label`, `remaining_seconds`, `stay_id`, `as_of`, `ticket_code`)
son **aditivos**: ningún cliente de v0.1 deja de funcionar.

## Reglas transversales verificadas

- **Mutaciones**: exigen `Origin` igual al origen propio **o** `Sec-Fetch-Site:
  same-origin`. La segunda señal existe porque `Referrer-Policy: no-referrer` hace
  que Chrome envíe `Origin: null` al enviar formularios del mismo origen; el
  navegador fija `Sec-Fetch-Site` y una página ajena no puede falsificarlo. Sin
  ninguna de las dos → 403 `ORIGIN_REQUIRED`.
- **Respuestas privadas** (código de reserva o ticket, páginas de consulta y ticket):
  `Cache-Control: no-store`. El código viaja en el cuerpo, nunca en la URL ni en logs.
- **Códigos**: 32 bytes aleatorios (`token_urlsafe`), digest SHA-256 en la base; el
  valor completo se entrega una sola vez. El QR contiene solo ese código, sin placa
  ni nombre. Código manual equivalente al QR en todas las operaciones.
- **Vencimiento**: `pending` con `expires_at <= now` se interpreta `expired` en
  cualquier lectura, sin tarea programada. Las escrituras normalizan (`expired` +
  liberación de la asignación) dentro de la transacción de asignación.
- **Concurrencia**: crear, cancelar y convertir usan `allocation_transaction` con
  sesión nueva; los UNIQUE y FK son la segunda defensa, no la única.

## Base (en `main`)

| Método / ruta | Entrada | Salida / acceso |
|---|---|---|
| GET `/health` | — | 200 `{status:"ok",database:"ok"}` con SELECT 1; 503 si BD inaccesible |
| GET `/` | — | HTML público con el estado real de las historias |
| GET `/acceso` | — | HTML login de personal |
| GET `/personal` | cookie | HTML protegido del personal autenticado |
| POST `/api/auth/login` | `{username,password}` + Origin | 200 usuario, Set-Cookie `plaza_session`; 401/422/429/403 |
| GET `/api/auth/me` | cookie | 200 `{id,username,role}` o 401 |
| POST `/api/auth/logout` | cookie + Origin | 204, revoca sesión y cookie; repetición 204 |

## HU-01 · disponibilidad y reserva (en `main`, PR #11)

| Método / ruta | Entrada | Salida |
|---|---|---|
| GET `/api/availability` | — | 200 `{as_of,preferential:{available,total},general:{available,total}}`; sin placas ni reservas |
| POST `/api/reservations` | `{plate}` + regla de origen | 201 `{status:"pending",space_code,plate,created_at,expires_at,private_code}`; 409 `PLATE_BUSY`/`CATEGORY_FULL`; 422 `VALIDATION_ERROR` |
| GET `/reservar` | — | HTML con capacidad efectiva y formulario |
| POST `/reservar` | formulario `plate` + regla de origen | HTML del resultado con espacio, vencimiento en America/Panama, código y QR SVG; errores 409/422 en la misma vista |

Placa: mayúsculas y recorte exterior, patrón `[A-Z0-9-]{2,12}` (D-04, propuesta
pendiente). Retención fija de 30 minutos desde `created_at`.

## HU-02 · consulta y cancelación privadas (en `main`, PR #12)

| Método / ruta | Entrada | Salida |
|---|---|---|
| POST `/api/reservations/lookup` | `{private_code}` | 200 `{status,status_label,plate,space_code,created_at,expires_at,cancelled_at,used_at,remaining_seconds}`; 404 `NOT_FOUND` genérico |
| POST `/api/reservations/cancel` | `{private_code}` + regla de origen | 200 mismo payload con estado terminal; 409 `RESERVATION_USED`; 404 genérico |
| GET `/mi-reserva` | — | HTML con formulario de código |
| POST `/mi-reserva` | formulario `private_code` + regla de origen | HTML del estado; 404 genérico en la misma vista |
| POST `/mi-reserva/cancelar` | formulario `private_code` + regla de origen | HTML del estado terminal |

`status` ∈ `pending`/`expired`/`cancelled`/`used`; `status_label` es la etiqueta en
español para la vista. `remaining_seconds` es 0 salvo `pending`. Repetir la
cancelación devuelve el mismo estado terminal con el `cancelled_at` original (D-05,
propuesta pendiente).

## HU-03 · ingreso en garita (PR #13, en revisión)

| Método / ruta | Entrada | Salida |
|---|---|---|
| POST `/api/entries/reservation` | celador/admin, `{private_code,plate}` + regla de origen | 201 `{status:"open",stay_id,space_code,plate,entered_at,as_of,ticket_code}`; 409 `RESERVATION_EXPIRED`/`RESERVATION_CANCELLED`/`RESERVATION_USED`/`PLATE_MISMATCH`/`PLATE_BUSY`; 404 genérico |
| POST `/api/entries/walk-in` | celador/admin, `{plate}` + regla de origen | 201 mismo payload; 409 `CATEGORY_FULL`/`PLATE_BUSY` |
| GET `/garita` | cookie celador/admin | HTML con capacidad y ambos formularios; 401 sin sesión, 403 rol sin garita |
| POST `/garita/reserva` | formulario `private_code,plate` + regla de origen | HTML del ticket imprimible con QR |
| POST `/garita/espontaneo` | formulario `plate` + regla de origen | HTML del ticket imprimible con QR |

Conversión: reserva `pending` vigente → estadía `open` + `used`, con la asignación
movida de `reservation_id` a `stay_id` en un solo commit. El espontáneo solo recibe
espacios `general`.

## Propuesto, todavía NO implementado (HU-04/HU-05, Alex)

| Historia | Método / ruta | Cuerpo / respuesta prevista |
|---|---|---|
| HU-04 | POST `/api/exits/quote` | celador/admin, `{ticket_code}` → estado/importe provisional/as_of; no muta |
| HU-04 | POST `/api/exits/close` | celador/admin, `{ticket_code,payment_confirmed:true}` + `Idempotency-Key` → 200 cierre con importe calculado en servidor a `exited_at` |
| HU-05 | GET `/api/alerts/long-stays` | vigilancia/celador/admin → placa, espacio, entered_at, elapsed_seconds, as_of |

Conflictos previstos: `STAY_CLOSED`, `IDEMPOTENCY_CONFLICT`. Idempotencia de cierre:
misma clave + mismo ticket devuelve el cierre original; misma clave + otro ticket →
409; reintentar un ticket ya cerrado devuelve su cierre original, sin pago ni salida
nuevos. El importe definitivo se calcula al confirmar; no se acepta cantidad del
navegador. Un QR cerrado jamás autoriza otro vehículo. Vistas previstas: `/salidas`,
`/vigilancia`.

## Preguntas abiertas (no son contrato)

- **Nombre del visitante**: la guía inicial (RN-03) dice «nombre y placa»;
  `data-model.md` excluye nombres y este contrato usa solo `{plate}`. Añadirlo exige
  decisión de Product/Spec y migración sucesora coordinada.
- **D-03/D-04/D-05**: aplicadas como propuesta documentada; pendientes de
  confirmación de Product/Spec.
- Revisar este contrato con el responsable de arquitectura; documentarlo no
  equivale a aprobación humana.
