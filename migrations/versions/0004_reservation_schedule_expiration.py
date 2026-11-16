"""Permite reservas demostrativas con una fecha programada anterior."""
from alembic import op

revision = "0004_reservation_schedule_expiration"
down_revision = "0003_roles_admin_client"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("PRAGMA foreign_keys=OFF")
    # Alembic/SQLite puede dejar este nombre temporal si una migración anterior
    # fue interrumpida antes de registrar la revisión. No contiene datos reales.
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_reservations")
    with op.batch_alter_table("reservations") as batch:
        batch.drop_constraint("expiration", type_="check")
        batch.create_check_constraint(
            "expiration", "scheduled_at IS NULL OR expires_at > scheduled_at")
    op.execute("PRAGMA foreign_keys=ON")


def downgrade():
    with op.batch_alter_table("reservations") as batch:
        batch.drop_constraint("expiration", type_="check")
        batch.create_check_constraint("expiration", "expires_at > created_at")
