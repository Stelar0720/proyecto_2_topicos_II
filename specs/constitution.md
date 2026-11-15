# Constitución v0.1

Fuente académica principal: `../DSaIA-Proyecto2.pdf`, pp. 1–3. Método complementario:
`../DSaIA-Tema9.pdf`, especialmente pp. 6, 9–18, 24–31. Ambos fueron extraídos y
leídos el 2026-11-15; los originales se conservan sin modificación.

Proyecto 2 exige explorar primero problema y outcomes, después SDD, código,
pruebas y valor al usuario. Tema 9 usa **ODD = Organic Driven Development**
(p. 30); no confundimos esa definición con el énfasis en resultados del proyecto.
Adoptamos especificaciones vivas, ligeras, versionadas y próximas historias detalladas.
Los ejemplos de cursos del material no son requisitos de Plaza Reserva.

- C-01: caso ficticio y metas como supuestos académicos; ninguna validación empresarial afirmada.
- C-02: una aplicación desplegable; Python/FastAPI, SQLAlchemy/Alembic, HTML/CSS/JS,
  pytest y Actions como propuesta técnica. SQLite local; PostgreSQL para publicación.
- C-03: integridad en servidor y BD, dinero en centavos, instantes UTC y reloj sustituible.
- C-04: trazabilidad outcome → requisito/regla → tarea → código → prueba → evidencia real.
- C-05: una historia completa por incremento; cada autor prueba su trabajo y solicita revisión.
- C-06: autenticación para personal, privacidad de visitantes y ausencia de secretos en logs.
- C-07: agentes limitados a su tarea; cambios compartidos coordinados; no inventar aceptación humana.
- C-08: este incremento crea solo la base. El cambio de mitad de desarrollo será aportado
  y documentado por el equipo cuando ocurra; no se simula evidencia retrospectiva.
