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
| RNF-01 | Evitar doble asignación, duplicación de placa y registros parciales bajo concurrencia | OUT-01/02/03 | HU-01/03/04 |
| RNF-02 | QR/códigos impredecibles, sin datos personales; acceso privado no enumerable | OUT-01/02 | HU-01/02/03 |
| RNF-03 | UTC persistido, America/Panama en vistas, reloj controlable, centavos enteros | OUT-03/04 | BASE-02/HU-04/05 |
| RNF-04 | Migración y carga de espacios reproducibles; pruebas y CI | OUT-05 | BASE-02/QA-01 |
| RNF-05 | Sin secretos/códigos completos en logs; errores sin datos ajenos | OUT-01/05 | Todas |

## Exclusiones acordadas

Sin horarios futuros, hora de salida contratada, cobro automático ni integración física.
Ampliación prevista **sin implementar**: recargos B/.25.00 por espacio reservado ajeno
y pérdida de ticket, incidencias por personal autorizado, recuperación por placa
conservando entrada original y prevención de recargos duplicados. Se especificará
el cambio concreto que aporte el equipo a mitad del desarrollo y se conservará su
evidencia real. Reconocimiento automático de placas: propuesta de fase 2.
