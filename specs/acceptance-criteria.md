# Criterios verificables

IDs estables. BASE se puede verificar en este incremento; HU/QA son pruebas futuras,
no resultados ya obtenidos. Detallar las historias posteriores justo antes de implementarlas.

| ID | Dado / Cuando / Entonces |
|---|---|
| AC-S01 | Dadas ambas fuentes y reglas acordadas, cuando reviso specs/backlog, entonces encuentro problema/outcomes como supuestos, IDs trazables, dependencias, exclusiones y distinción ODD sin afirmar aprobación humana. |
| AC-B01 | Dada BD migrada, cuando consulto salud, entonces responde 200 y comprueba conexión; si no responde la BD, 503 sin secretos. |
| AC-B02 | Dada BD vacía migrada, cuando ejecuto seed dos veces, entonces hay exactamente P001–P020 y G001–G080; no se borran datos existentes. |
| AC-B03 | Dado acceso sin sesión, cuando consulto `/personal` o `/api/auth/me`, entonces 401 sin datos de personal. |
| AC-B04 | Dado personal creado por CLI, cuando autentica correctamente, entonces recibe sesión privada; vencida/revocada/inactiva ya no accede. |
| AC-B05 | Dada petición mutante sin Origin o de otro origen, cuando intenta login/logout, entonces 403; credenciales erróneas dan 401 genérico. |
| AC-B06 | Dada base, cuando abro navegación, entonces las historias pendientes están identificadas y no hay endpoints de parking que simulen éxito. |
| AC-01 | Dados preferenciales disponibles, cuando reservo placa libre, entonces retengo uno por 30 min y recibo QR y código sin datos personales en QR. |
| AC-02 | Dado último preferencial, cuando dos conexiones reservan simultáneamente placas distintas, entonces solo una tiene éxito y la otra 409; no hay filas parciales. |
| AC-03 | Dada reserva pendiente, cuando reloj llega exactamente a expires_at o lo supera, entonces la disponibilidad la ignora sin cron y no permite ingreso. |
| AC-04 | Dado código privado válido, cuando consulto/cancelo, entonces veo solo mi reserva; cancelación libera y no permite ingreso; código inválido responde genéricamente sin enumeración. |
| AC-05 | Dada reserva vigente y placa verificada, cuando celador confirma ingreso, entonces reserva usada y estadía abierta/asignación se escriben atómicamente; fallo revierte todo. |
| AC-06 | Dado último general disponible, cuando dos ingresos espontáneos compiten, entonces uno entra y recibe ticket imprimible; el otro 409 sin usar preferenciales ni crear registros parciales. |
| AC-07 | Dada placa con reserva pendiente o estadía abierta, cuando intenta otra asignación, entonces 409 sin duplicación; probar también dos peticiones concurrentes de misma placa. |
| AC-08 | Dada reserva vencida/cancelada/usada, cuando reintento ingreso por QR o código manual, entonces se rechaza; ambos mecanismos respetan el mismo contrato. |
| AC-09 | Dada entrada y reloj controlados, cuando transcurren 0s/1s/60s/60s+1µs/65min, entonces el importe es 0/2/2/4/130 centavos respectivamente (D-06). |
| AC-10 | Dada estadía abierta, cuando celador confirma pago/salida y reintenta incluso concurrentemente, entonces hay un solo pago y cierre original, y espacio liberado una vez. |
| AC-11 | Dado ticket de estadía cerrada, cuando se reutiliza mientras otro vehículo ocupa ese espacio, entonces no cierra ni cobra la estadía nueva. |
| AC-12 | Dada estadía abierta de 24h−1µs/24h/24h+1µs, cuando consulto alertas, entonces solo la última aparece con placa/espacio/duración, sin recargo/liberación; cerradas excluidas. |
| AC-13 | Dado visitante o rol no permitido, cuando invoca operación protegida, entonces 401/403; no datos ajenos ni códigos completos en logs/errores. |
| AC-14 | Dada BD demo separada y referencia fija, cuando cargo dos veces, entonces existen los seis escenarios acordados sin duplicados ni borrado de datos ajenos. |

AC-01–08 son el primer detalle operativo próximo: HU-01 → HU-02 → HU-03.
Alex refinará AC-09–14 antes de implementar HU-04/05/QA-01, conservando fronteras.
