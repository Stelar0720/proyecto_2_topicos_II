# Plan de implementación por incrementos

1. BASE-01: problema/outcomes → requisitos y reglas → contratos ligeros → backlog.
2. BASE-02: migración/modelos comunes, auth, salud/layout, seed estático, tests y CI.
   Verificar y someter a revisión; integrar en main por decisión humana.
3. Francisco: HU-01 disponibilidad/reserva/QR completa; luego HU-02 consulta/cancelación;
   luego HU-03 ingreso reservado/espontáneo y ticket. No entregar solo capas.
4. Alex: puede refinar HU-04 mientras espera HU-03; implementación de salida/cobro/pago
   requiere el ingreso integrado. Después HU-05 y QA-01 demo/integración.
5. CAMBIO-01: tras solicitud confirmada, especificar RF-11/BR-34–37/AC-18,
   migrar pago, implementar cotejo de salida y probar multa única/idempotencia.
6. ENTREGA-01: Jack coordina publicación posterior y Alex reproducibilidad/CI.
   Probar PostgreSQL realmente antes de declarar soporte, decidir hosting sin contratarlo aquí.

Cada incremento: leer → refinar criterios → coordinar contratos → rama pequeña →
implementar historia → probar sus criterios → actualizar trazabilidad/ai-log → PR →
revisión humana → integración. `En revisión` no significa `Terminado` ni aceptación.

CAMBIO-01 es el cambio concreto confirmado el 2026-11-16. La solicitud y confirmación
se registran en `requirements.md`; antes de código se actualizaron requisitos, reglas,
criterios, plan y tareas. Solo este recargo por discordancia está implementado.

Roles rotativos y responsables de entregas están en `docs/team-plan.md`.
