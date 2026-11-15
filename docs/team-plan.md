# Equipo y coordinación

Jack: outcomes/ODD, arquitectura, contratos, base, migraciones e integración y
configuración de publicación posterior. Francisco: disponibilidad, reserva/consulta/
cancelación, QR digital, ingreso reservado/espontáneo y ticket, con sus pruebas.
Alex: salida/cobro/pago, alerta, datos demo, coordinación de CI e integración y
pruebas de sus historias. Alex **no** es responsable de probar todo el código de Francisco.

| Ciclo | Product / Spec | Architecture / Development | QA / DevOps |
|---|---|---|---|
| 1 | Jack | Francisco | Alex |
| 2 | Alex | Jack | Francisco |
| 3 | Francisco | Alex | Jack |

Son **roles asignados**, no evidencia de trabajo ya realizado. Las entregas propias
siguen a cargo de los responsables indicados aunque rote el liderazgo.

## Incorporación

1. Jack prepara BASE-01/02 y un PR. Revisar/integrar base en main antes de iniciar historias.
2. Francisco actualiza main y crea `feature/hu-01-reservas`; HU-01 → HU-02 → HU-03.
3. Alex actualiza main y revisa HU-04/05, CI y demo. Puede refinar criterios/CI
   coordinadamente; implementar salidas/alertas requiere HU-03 integrado. Después QA-01.
4. Cada uno abre PR pequeño con criterios, pruebas y evidencia real. No recrear tablero/base.

## Archivos compartidos

Jack coordina `models.py`, `db.py`, `config.py`, `auth.py`, `security.py`, `main.py`,
`cli.py`, `clock.py`, `errors.py`, `templates/base.html`, `static/app.css`,
`pyproject.toml`, `.env.example`, `alembic.ini`, `migrations/` y `specs/`.
Alex coordina `.github/workflows/ci.yml` con Jack. Antes de editar, comentar en el
issue o coordinar directamente y registrar lo realmente acordado. No se afirma
que esos comentarios/conversaciones ya existan.

Cada historia agrega sus módulos y vistas; integración de router en main se coordina.
Cambios de esquema: propuesta → contrato → migración sucesora → prueba de ambos
motores → revisión de Jack. No editar 0001 después de integrarla ni generar heads paralelas.

DoD: historia end-to-end, criterios y pruebas propias, documentación/traza actualizadas,
PR revisado y aceptación humana registrada. Una ejecución del agente no es aceptación.
