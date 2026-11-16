# Requisitos v0.1

Reglas exactas en `business-rules.md`; criterios en `acceptance-criteria.md`.
Todos los requisitos funcionales están **pendientes**, salvo fundamentos BASE que
se describen en README y cuya verificación real figura en `docs/testing.md`.

| ID | Comportamiento | Outcome | Historia |
|---|---|---|---|
| RF-01 | Mostrar disponibilidad efectiva por categoría sin datos personales | OUT-01 | HU-01 |
| RF-02 | Crear reserva preferencial de llegada próxima por 30 min y entregar QR/código privado | OUT-01 | HU-01 |
| RF-03 | Consultar/cancelar solo mediante credencial privada | OUT-01 | HU-02 |
| RF-04 | Celador verifica placa y convierte reserva vigente en estadía atómicamente | OUT-02 | HU-03 |
| RF-05 | Celador registra espontáneo en general disponible y obtiene ticket QR imprimible | OUT-02 | HU-03 |
| RF-06 | Calcular desde entrada real, cobrar manualmente y cerrar una sola vez | OUT-03 | HU-04 |
| RF-07 | Mostrar placa, espacio y duración de estadías abiertas de más de 24 h | OUT-04 | HU-05 |
| RF-08 | Autenticar personal de garita, vigilancia y administración | OUT-02/03/04 | BASE-02 |
| RF-09 | Permitir a clientes demo programar una reserva con nombre, placa y fecha/hora seleccionada | OUT-01 | DEMO-UX |
| RF-10 | Mostrar al administrador el estado visual de los 100 espacios y permitir escanear QR de entrada/salida | OUT-02/03/04 | DEMO-UX |
| RF-11 | En salida, cotejar QR con placa y espacio declarados; si no coinciden, aplicar y registrar multa manual de B/.25.00 | OUT-03 | CAMBIO-01 |
| RNF-01 | Evitar doble asignación, duplicación de placa y registros parciales bajo concurrencia | OUT-01/02/03 | HU-01/03/04 |
| RNF-02 | QR/códigos impredecibles, sin datos personales; acceso privado no enumerable | OUT-01/02 | HU-01/02/03 |
| RNF-03 | UTC persistido, America/Panama en vistas, reloj controlable, centavos enteros | OUT-03/04 | BASE-02/HU-04/05 |
| RNF-04 | Migración y carga de espacios reproducibles; pruebas y CI | OUT-05 | BASE-02/QA-01 |
| RNF-05 | Sin secretos/códigos completos en logs; errores sin datos ajenos | OUT-01/05 | Todas |

## Exclusiones acordadas

Sin hora de salida contratada, cobro automático ni integración física. Para la demo,
las reservas admiten una fecha/hora pasada o futura elegida manualmente; la ventana
de llegada dura 30 minutos desde esa hora. El cobro inicia al registrar el ingreso,
no al programar la reserva.
Cambio de requisito CAMBIO-01 confirmado por el usuario el 2026-11-16: en salida
se capturan placa y espacio observados junto al QR. Si alguno no coincide con la
estadía identificada por el QR, se suma y registra una multa de B/.25.00. No se
aplican multas por pérdida de ticket, recargos por otros motivos, incidencias ni
recuperación por placa. Reconocimiento automático de placas: propuesta de fase 2.
