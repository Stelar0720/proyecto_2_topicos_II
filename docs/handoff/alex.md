# Handoff de Alex

Dependencia de base: BASE-02 integrado realmente en main. Dependencia funcional:
HU-03 para salidas/alertas; HU-01–05 para demo integrada. Se puede revisar el diseño
y coordinar CI antes, sin simular datos/historias terminadas.

## Miniprompt copiable para tu Codex

```text
Trabaja en proyecto_2_topicos_II, Plaza Reserva, como apoyo de Alex.
Lee AGENTS.md, README.md, specs/constitution.md, outcomes.md, requirements.md,
business-rules.md, architecture.md, data-model.md, api.md, acceptance-criteria.md,
implementation-plan.md, tasks.md, docs/testing.md, team-plan.md y traceability.md.

Comprueba estado Git y conserva cambios. Espera BASE-02 integrado en main y parte
de ese commit real: git fetch origin, git switch main, git pull --ff-only origin main.
Con copia limpia crea feature/hu-04-salidas. HU-04/HU-05 requieren HU-03 integrado;
puedes refinar criterios/CI coordinadamente antes. No reconstruyas base ni tablero.
Consulta docs/github-state.json: sin URL no inventes issue ni PR; usa IDs estables.
Tu cuenta GitHub aún no está verificada: no autoasignes a una cuenta supuesta.

Orden: HU-04 T-04A/B (salida/cálculo/pago manual); HU-05 T-05A (alerta >24h);
QA-01 T-QA1/2 (demo separada/integración); apoya ENTREGA-01/CI con Jack.
Cada historia es punta a punta: interfaz, API, lógica, datos, pruebas y evidencia.
No eres responsable de probar todo el código de Francisco: él entrega sus pruebas.

Base real: src/plaza_reserva/{main,config,db,clock,models,auth,security,errors,cli}.py,
templates/base.html, static/app.css, migrations/versions/0001_shared_base.py,
tests/conftest.py y workflow ci.yml. No hay lógica de salida, cobro, alerta o demo.
Módulos futuros previstos exits.py, alerts.py, demo.py, templates/exits/ y
templates/alerts/, tests/test_exits.py, test_alerts.py e integration/.
Coordina main.py para agregar routers. Respeta contratos propuestos:
POST /api/exits/quote, POST /api/exits/close con Idempotency-Key,
GET /api/alerts/long-stays; hoy NO existen.

Usa Clock.now() inyectable; captura instante una vez. UTC persistido y America/Panama
en vistas. Cobro: 2 centavos/minuto desde entrada real, fracción al minuto superior,
aritmética entera (microsegundos); revisa D-06 con Product/Spec antes de implementar.
Sin salida contratada. Calcula definitivo al confirmar; no aceptes importe del cliente.
Pago manual, un payment por stay y clave idempotente única. Cierre libera allocation
y escribe pago/closed/exited_at en una transacción usando allocation_transaction
con sesión nueva. Reintento devuelve cierre original; clave reutilizada con otro
ticket da conflicto; QR cerrado no puede afectar al nuevo ocupante del espacio.
Alerta estricta >24h, abierta, placa/espacio/duración; sin recargo ni liberación.
Usa current_staff/require_roles y same_origin de auth; nunca secretos en logs.

Archivos compartidos: modelos, migraciones, config/db/auth/security/clock/main/cli,
layout, CSS, dependencias y specs coordinados con Jack. CI lo coordinas con Jack.
No reescribas 0001 integrada; cambios llevan migración sucesora revisada.

Prueba AC-09–14/13: 0/1/60/60+1µs/3900 segundos, reloj controlado, reintentos
concurrentes de cierre/pago, ticket cerrado contra otro ocupante, alerta antes/a/después
de 24h, cerradas excluidas, permisos. Integra las carreras/pruebas propias de Francisco.
Usa pytest, SQLite de archivo y PostgreSQL real en BD descartable terminada _test.

Demo: implementa después seed-demo idempotente en BD separada, referencia común
2026-11-15T17:00:00Z y las seis filas de docs/testing.md. Sin placas/espacios repetidos,
sin borrar datos ajenos. No hay comando demo en base: no aparentes que ya funciona.
No implementes recargos B/.25, incidencias, recuperación por placa ni ALPR. La
ampliación concreta llegará del equipo a mitad del desarrollo; conserva evidencia real.

Commits/PR pequeños con ID. Actualiza spec/traceability/ai-log, reporta comandos y
resultados reales. No cierres issues como aceptados ni inventes revisiones. No fusiones
PR ni publiques/contrates servicios; Jack coordina publicación en el paso posterior.
```
