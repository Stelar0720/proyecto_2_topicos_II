"""Registra la multa por discordancia entre QR, placa y espacio."""
from alembic import op
import sqlalchemy as sa


revision = "0006_exit_mismatch_fee"
down_revision = "0005_access_codes_for_dashboard"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payments") as batch:
        batch.add_column(sa.Column("mismatch_fee_cents", sa.Integer(), nullable=False,
                                   server_default="0"))
        batch.create_check_constraint("nonnegative_mismatch_fee", "mismatch_fee_cents >= 0")


def downgrade():
    with op.batch_alter_table("payments") as batch:
        batch.drop_constraint("nonnegative_mismatch_fee", type_="check")
        batch.drop_column("mismatch_fee_cents")
