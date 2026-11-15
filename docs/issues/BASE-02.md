# BASE-02: esqueleto y contratos compartidos

## Historia u objetivo

Config, BD, modelos/migración, auth, salud, layout, seed, pruebas y CI.

Responsable previsto: **Jack**. Assignee GitHub pendiente de usuario verificado.
Outcome: OUT-05. Requisitos: RF-08, RNF-01/03/04/05. Fuente: specs/tasks.md y specs/requirements.md.

## Alcance

Config, BD, modelos/migración, auth, salud, layout, seed, pruebas y CI.

## Exclusiones

Sin flujos completos de reservas, ingresos, salidas, cobros o alertas.

## Criterios Dado/Cuando/Entonces

- **AC-B01**: Dada BD migrada, cuando consulto salud, entonces responde 200 y comprueba conexión; si no responde la BD, 503 sin secretos.
- **AC-B02**: Dada BD vacía migrada, cuando ejecuto seed dos veces, entonces hay exactamente P001–P020 y G001–G080; no se borran datos existentes.
- **AC-B03**: Dado acceso sin sesión, cuando consulto `/personal` o `/api/auth/me`, entonces 401 sin datos de personal.
- **AC-B04**: Dado personal creado por CLI, cuando autentica correctamente, entonces recibe sesión privada; vencida/revocada/inactiva ya no accede.
- **AC-B05**: Dada petición mutante sin Origin o de otro origen, cuando intenta login/logout, entonces 403; credenciales erróneas dan 401 genérico.
- **AC-B06**: Dada base, cuando abro navegación, entonces las historias pendientes están identificadas y no hay endpoints de parking que simulen éxito.

## Dependencias

BASE-01. No iniciar implementación dependiente antes de integrar su base real.

## Pruebas esperadas

Migración upgrade/downgrade, seed repetido, auth y salud; SQLite y PG. Registrar comandos, resultado y motor reales. Prueba escrita no es prueba aprobada.

## Archivos o módulos previstos

src/, migrations/, tests/, .github/, pyproject.toml. Coordinar archivos compartidos con Jack; CI con Alex. Los módulos de
historias todavía no existen en el esqueleto. Consultar handoff correspondiente.

## Condición de terminado

Criterios verificados, historia completa cuando corresponda, pruebas propias,
contratos/especificación/trazabilidad/ai-log actualizados, PR revisado e integrado
y aceptación humana registrada. En revisión no equivale a Terminado.
No inventar entrevistas, revisiones, métricas, resultados ni actividad Git.
