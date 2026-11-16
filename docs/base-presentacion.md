# Base para presentación - Plaza Reserva

Duración objetivo: aproximadamente 10 minutos. Esta guía separa evidencia
verificable de resultados previstos; no es un PPT.

## Diapositiva 1 - Problema y propuesta de valor

- Plaza ficticia: 20 preferenciales y 80 generales.
- Control manual puede provocar cruces, ocupación confusa y cobros inconsistentes.
- Plaza Reserva organiza reserva, ingreso, salida y alerta.
- Objetivo: demostrar un flujo trazable, no prometer métricas comerciales.

Notas: Explicar que el problema y beneficios son supuestos académicos, no entrevistas
ni mediciones de una plaza real. Presenta al visitante, al administrador/celador y a
vigilancia como actores definidos en `specs/outcomes.md`.

## Diapositiva 2 - Outcomes y alcance final

- OUT-01: reservar o informar falta de cupo.
- OUT-02: registrar ingreso sin duplicar placa ni espacio.
- OUT-03/04: cobrar, cerrar y alertar estadías >24 h.
- Excluidos: barreras, sensores, pasarela y recuperación por placa.

Notas: Señalar que el QR es una ayuda de entrada/salida y el código manual siempre
es alternativa. Aclarar que 20/80 son capacidades, no disponibilidad en tiempo real.

## Diapositiva 3 - Reglas de negocio demostrables

- Reserva preferencial dura 30 min desde la fecha/hora programada.
- Un QR privado identifica la misma visita en entrada y salida.
- Cobro: B/.0.02/minuto desde ingreso real; fracción redondea arriba.
- Dashboard: gris disponible, verde reservado/ocupado, rojo alerta >24 h.
- Discordancia QR/placa/espacio en salida: multa única de B/.25.00.

Notas: Mencionar BR-01 a BR-33. La alerta no libera espacio ni aplica recargo. El
ticket cerrado no puede afectar una nueva estadía.

## Diapositiva 4 - Arquitectura y stack real

- FastAPI + Jinja/HTML/CSS/JavaScript de mismo origen.
- Servicios por dominio: reservas, ingresos, salidas, alertas y demo.
- SQLAlchemy + Alembic; SQLite local y PostgreSQL previsto.
- Pytest, workflow GitHub Actions y QR SVG/local.

Notas: Justificar arquitectura simple: 100 espacios y una fila de guarda para
serializar asignaciones. No afirmar que PostgreSQL o CI pasaron: están pendientes
de prueba actual.

## Diapositiva 5 - Recorrido ODD -> SDD -> código -> prueba

- Outcome: evitar doble asignación de un preferencial.
- SDD: RF-02, BR-10 a BR-14 y AC-02.
- Código: `reservations.py`, `allocations`, transacción de asignación.
- Prueba actual: carrera de último preferencial, PASS (1 ganador, 20 asignaciones).

Notas: Este es el ejemplo más sólido para mostrar el método. Indicar que en la
auditoría se detectó y corrigió que una reserva no creaba `Allocation`; la carrera
repetida pasó después de la corrección. Es evidencia técnica, no aceptación humana.

## Diapositiva 6 - Equipo, Git e IA

- Plan de rotación: Jack/Francisco/Alex en Product, Desarrollo y QA por ciclos.
- Git local conserva PR merges #10 a #14 y ramas de historias.
- `ai-log.md` registra actividad, solicitud, resultado y decisión.
- Autores verificables: Jack y Alex tienen commits nominales; parte de HU-01/03 usa identidad genérica.

Notas: No atribuir automáticamente los commits `Your New Name` a una persona. La
rotación está documentada como plan, no como prueba completa de actividad histórica.
La IA apoyó lectura, especificaciones, código, pruebas y auditoría; las decisiones
humanas deben quedar registradas por el equipo.

## Diapositiva 7 - Pruebas y cambio de requisito

- Hoy: 79 pruebas recolectadas; integración SQLite 3/3 PASS.
- Pruebas cubiertas hoy: último general, último preferencial y seed demo idempotente.
- Cambio: cotejo QR, placa y espacio; multa única de B/.25.00.
- Traza: migración 0006, RF-11, BR-34/37, AC-18, salida y prueba integrada.

Notas: La suite HTTP completa sigue pendiente: varios tests usan roles y payloads
anteriores. La solicitud y confirmación del cambio fueron registradas en la
especificación; aún falta una revisión humana. No afirmar 79 passed hoy.

## Diapositiva 8 - Limitaciones, siguiente paso y reparto de exposición

- Falta ejecutar suite HTTP actualizada, PostgreSQL y CI remoto.
- Falta evidencia viva de GitHub Project/estado de issues y revisión humana.
- Ensayar QR/cámara en Chrome o Edge y flujo completo con datos ficticios.
- Reparto sugerido: Jack 1-3, Francisco 4-5, Alex 6-8.

Notas: El reparto es para equilibrar la presentación, no declara quién hizo cada
parte históricamente. Si el profesor escoge a alguien al azar, todos deben conocer
las ocho diapositivas y la lista de limitaciones.

