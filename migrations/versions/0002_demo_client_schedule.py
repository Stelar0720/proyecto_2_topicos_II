"""Demo UX: roles admin/client y reservas programadas."""
from alembic import op
import sqlalchemy as sa

revision = "0002_demo_client_schedule"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("reservations") as batch:
        batch.add_column(sa.Column("customer_name", sa.String(80), nullable=True))
        batch.add_column(sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE reservations SET customer_name = 'Cliente demo', scheduled_at = created_at WHERE scheduled_at IS NULL")


def downgrade():
    with op.batch_alter_table("reservations") as batch:
        batch.drop_column("scheduled_at")
        batch.drop_column("customer_name")
