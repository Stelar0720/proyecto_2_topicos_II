# Guion de demostración - Plaza Reserva

Usar una base de demostración descartable y cuentas autorizadas creadas localmente.
No proyectar contraseñas, tokens, códigos QR completos ni datos personales. Reemplazar
los valores entre corchetes por datos ficticios visibles solo para el ensayo.

## Preparación

1. Confirmar migración aplicada y 100 espacios: P001-P020 y G001-G080.
2. Iniciar sesión como `[admin de demo]`; abrir `/cliente`, `/garita`, `/salidas`,
   `/vigilancia` y `/personal` en pestañas controladas.
3. Tener dos placas ficticias disponibles, por ejemplo `DEM100` y `DEM200`.
4. Usar el formulario manual como respaldo si la cámara del navegador no está
   disponible; no simular que la cámara leyó un QR si no ocurrió.

## 1. Reserva programada

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | Como cliente, elegir nombre ficticio, placa `DEM100` y hora de llegada actual o próxima. | Se crea una reserva preferencial con espacio y QR/código privado. |
| 2 | Mostrar la fecha/hora y el aviso de 30 minutos. | La retención se calcula desde la hora programada, no desde el momento de pago. |
| 3 | Consultar `Mi reserva` con el código. | Solo aparece esa reserva; no se enumeran reservas ajenas. |
| 4 | Mostrar dashboard admin. | El espacio aparece verde mientras la reserva esté vigente. |

## 2. Ingreso con el mismo QR

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | En `/garita`, escanear el QR de la reserva o escribir el código privado. | Se valida la reserva y la placa. |
| 2 | Confirmar ingreso de `DEM100`. | Reserva `used`, estadía `open`, ticket con el mismo QR/código. |
| 3 | Mostrar ticket y hora de ingreso. | El cobro comienza en esa hora real. |
| 4 | Reintentar el mismo QR en entrada. | Rechazo: reserva/ticket ya utilizado para ingreso. |

## 3. Ingreso sin reserva y capacidad

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | En `/garita`, registrar placa `DEM200` como espontáneo. | Se asigna un espacio general, nunca uno preferencial. |
| 2 | Mostrar dashboard. | El general se ve verde; los libres permanecen grises. |
| 3 | Intentar otra entrada con `DEM200`. | Rechazo de placa con estadía abierta. |

## 4. Cobro y salida

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | En `/salidas`, leer el QR/código del ticket de `DEM100`. | Cotización sin modificar la estadía. |
| 2 | Explicar la tarifa B/.0.02/minuto y el redondeo al minuto superior. | El importe mostrado se calcula desde la entrada real. |
| 3 | Confirmar pago manual y salida. | Pago registrado, estadía cerrada y espacio liberado. |
| 4 | Reintentar la salida con el ticket ya cerrado. | No se crea un segundo pago ni se afecta otra estadía. |

## 5. Alerta mayor de 24 horas

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | Cargar únicamente datos demo aprobados o crear una estadía ficticia con más de 24 h en una BD descartable. | Existe una estadía `open` de más de 24 h. |
| 2 | Abrir `/vigilancia` y `/personal`. | Se muestra placa/espacio/duración; el espacio está rojo. |
| 3 | Comparar con una estadía exactamente de 24 h si se dispone del dato demo. | Exactamente 24 h no activa alerta; la regla es estrictamente mayor. |
| 4 | Señalar que no se cobra multa ni se libera automáticamente. | La alerta es informativa. |

## 6. Rechazo de doble reserva

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | Usar dos clientes/pestañas con una fecha/hora que se solape y los últimos cupos preferenciales. | Solo una reserva debe aceptar el último espacio. |
| 2 | En la otra pestaña enviar la solicitud casi al mismo tiempo. | Conflicto de categoría llena o placa ocupada, sin registro parcial. |
| 3 | Revisar disponibilidad/dashboard. | No hay dos vehículos en el mismo espacio. |

## Cierre de la demo

- Mostrar que multas, incidencias y recuperación por placa están fuera de alcance.
- Indicar qué se ejecutó realmente en la auditoría: carrera de último preferencial,
  último general y seed demo idempotente en SQLite.
- Declarar como pendiente la suite HTTP actualizada, PostgreSQL, CI remoto y la
  revisión humana; no sustituirlos con capturas o resultados históricos.

