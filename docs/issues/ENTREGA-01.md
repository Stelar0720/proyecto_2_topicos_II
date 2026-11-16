# ENTREGA-01: ejecución reproducible y publicación/demo

## Historia u objetivo

Ensayo reproducible, evidencia académica, PostgreSQL realmente ejecutado y publicación posterior coordinada.

Responsable previsto: **Jack con Alex**. Assignee GitHub pendiente de usuario verificado.
Outcome: OUT-05. Requisitos: RNF-04/05; requisitos académicos Proyecto 2. Fuente: specs/tasks.md y specs/requirements.md.

## Alcance

Ensayo reproducible, evidencia académica, PostgreSQL realmente ejecutado y publicación posterior coordinada.

## Exclusiones

No contratar ni desplegar en la preparación inicial; no inventar cambios a mitad del desarrollo.

## Criterios Dado/Cuando/Entonces

- **AC-B01**: Dada BD migrada, cuando consulto salud, entonces responde 200 y comprueba conexión; si no responde la BD, 503 sin secretos.
- **AC-B02**: Dada BD vacía migrada, cuando ejecuto seed dos veces, entonces hay exactamente P001–P020 y G001–G080; no se borran datos existentes.
- **AC-B03**: Dado acceso sin sesión, cuando consulto `/personal` o `/api/auth/me`, entonces 401 sin datos de personal.
- **AC-14**: Dada BD demo separada y referencia fija, cuando cargo dos veces, entonces existen los seis escenarios acordados sin duplicados ni borrado de datos ajenos.

## Dependencias

QA-01; decisiones de hosting/seguridad y revisión humana. No iniciar implementación dependiente antes de integrar su base real.

## Pruebas esperadas

Instalación limpia, migración/seed, pytest/CI, demo; registrar URL real solo si se publica. Registrar comandos, resultado y motor reales. Prueba escrita no es prueba aprobada.

## Archivos o módulos previstos

README.md, docs/testing.md, .github/, configuración de publicación posterior. Coordinar archivos compartidos con Jack; CI con Alex. Los módulos de
historias todavía no existen en el esqueleto. Consultar handoff correspondiente.

## Condición de terminado

Criterios verificados, historia completa cuando corresponda, pruebas propias,
contratos/especificación/trazabilidad/ai-log actualizados, PR revisado e integrado
y aceptación humana registrada. En revisión no equivale a Terminado.
No inventar entrevistas, revisiones, métricas, resultados ni actividad Git.
