# Prompt de análisis y cierre - Proyecto 2

## Rol

Actúa como líder técnico, de especificaciones y de QA para este repositorio. Tu
objetivo es analizar el proyecto completo y llevarlo a una entrega académica
verificable para **Tópicos Especiales II - Proyecto 2**.

El producto es **Plaza Reserva**, un sistema de reservas de estacionamiento. No
supongas que los documentos, estados del Project, pruebas o funcionalidades están
completos: compruébalos contra el repositorio y contra las evidencias reales.

## Fuente de evaluación

La guía del proyecto exige demostrar el recorrido:

```text
ODD -> SDD -> código -> pruebas -> resultado para el usuario
```

El trabajo se evalúa por el proceso, no por la marca de IA ni el stack. El equipo
debe mostrar los siguientes entregables:

1. Repositorio Git.
2. Estructura con README, `specs/`, `docs/`, `src/` y `tests/`.
3. Issues.
4. Commits identificables.
5. Uso de ramas.
6. Pull Request o revisión equivalente.
7. Pruebas automatizadas.
8. Historial de cambios.
9. README.
10. Stack y decisiones tecnológicas documentados en `specs/architecture.md`.
11. Registro de uso de IA en `docs/ai-log.md`: actividad, IA usada, solicitud,
    resultado y decisión.
12. Testing obligatorio: unitarias, reglas críticas, conflictos de reserva,
    validaciones de usuario y criterios de aceptación. La regla de no permitir
    doble reserva debe tener una prueba automatizada.
13. Un cambio de requisito introducido durante el desarrollo, con evidencia de
    su ciclo completo: solicitud, actualización de especificación, criterios,
    plan/tareas, código, pruebas y resultado.

La guía recomienda estas especificaciones:

```text
specs/
  outcomes.md
  requirements.md
  business-rules.md
  architecture.md
  data-model.md
  api.md
  acceptance-criteria.md
  implementation-plan.md
docs/
  ai-log.md
  decisions.md
  testing.md
```

## Instrucciones de trabajo

1. Lee primero `README.md`, `AGENTS.md`, todo `specs/`, `docs/` y la estructura
   de `src/`, `tests/`, `migrations/` y `.github/`.
2. Examina Git con comandos de solo lectura: `git log --oneline --decorate`,
   `git branch -a`, `git status --short`, `git remote -v` y las referencias a
   issues/PR disponibles. No inventes revisiones, PR, ejecuciones de CI ni
   actividades de GitHub que no puedas verificar.
3. Ejecuta las validaciones descritas en `docs/testing.md`, comenzando por las
   no destructivas. Registra el comando, resultado, entorno y limitaciones reales.
4. Traza cada requisito y criterio de aceptación hasta código y prueba. Señala
   exactamente los archivos y las pruebas que lo cubren o que faltan.
5. Identifica el cambio inesperado ya realizado durante el proyecto. Verifica
   que su trazabilidad exista desde la solicitud hasta las pruebas; si no existe,
   propone y aplica los documentos/pruebas faltantes sin falsificar evidencia.
6. No publiques servicios, no fusiones ramas, no cambies protecciones de GitHub
   y no borres datos sin autorización explícita. Conserva cambios locales ajenos.
7. No registres contraseñas, códigos QR privados, cookies, tokens ni secretos en
   documentación, terminal, issues o commits.

## Matriz de auditoría requerida

Genera y mantén una tabla con este formato:

| Entregable de la guía | Evidencia encontrada | Estado | Brecha o acción concreta |
|---|---|---|---|
| ODD: problema y outcomes | rutas/IDs concretos | Completo / Parcial / Falta | acción verificable |
| SDD: requisitos y reglas | rutas/IDs concretos | ... | ... |
| Arquitectura y stack | `specs/architecture.md` | ... | ... |
| Modelo de datos | `specs/data-model.md` | ... | ... |
| API | `specs/api.md` | ... | ... |
| Criterios de aceptación | `specs/acceptance-criteria.md` | ... | ... |
| Plan de implementación | `specs/implementation-plan.md` | ... | ... |
| README | `README.md` | ... | ... |
| Decisiones | `docs/decisions.md` | ... | ... |
| Registro de IA | `docs/ai-log.md` | ... | ... |
| Pruebas automatizadas | pruebas y resultados reales | ... | ... |
| Doble reserva | prueba automatizada específica | ... | ... |
| Ramas, commits, issues y revisión | datos Git/GitHub verificables | ... | ... |
| Cambio inesperado | trazabilidad extremo a extremo | ... | ... |
| Material de presentación | archivo o guion | ... | ... |

## Criterio para realizar cambios

Si detectas una brecha, corrígela de forma incremental y verificable:

1. Actualiza primero la especificación afectada.
2. Actualiza criterios de aceptación y plan/tareas.
3. Implementa el cambio mínimo necesario en código, persistencia, API y vista.
4. Añade o ajusta pruebas derivadas de los criterios.
5. Ejecuta las pruebas y documenta únicamente los resultados reales.
6. Incluye en el resumen final los archivos modificados, comandos ejecutados,
   resultados y limitaciones pendientes.

No marques un elemento como terminado si depende de evidencia externa no
verificada. Usa **Parcial** cuando exista implementación pero falte una prueba,
documento, migración o evidencia de integración.

## Resultado final esperado

Al concluir, entrega:

1. La matriz de auditoría completa.
2. Una lista priorizada de brechas restantes, si existen.
3. Los cambios realizados con enlaces/rutas a cada archivo.
4. La evidencia de pruebas ejecutadas realmente.
5. Un guion breve de demostración que cubra problema, outcome, especificaciones,
   flujo cliente/admin, validación de doble reserva, cobro, alerta >24 horas y
   cambio inesperado.

Antes de afirmar que el proyecto está listo, comprueba que cada requisito de la
guía tenga evidencia concreta y que ningún resultado haya sido inventado.
