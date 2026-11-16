"""Conserva el código QR para consulta rápida del administrador."""
from alembic import op
import sqlalchemy as sa

revision = "0005_access_codes_for_dashboard"
down_revision = "0004_reservation_schedule_expiration"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("reservations") as batch:
        batch.add_column(sa.Column("access_code", sa.String(128), nullable=True))
    with op.batch_alter_table("stays") as batch:
        batch.add_column(sa.Column("access_code", sa.String(128), nullable=True))


def downgrade():
    with op.batch_alter_table("stays") as batch:
        batch.drop_column("access_code")
    with op.batch_alter_table("reservations") as batch:
        batch.drop_column("access_code")
