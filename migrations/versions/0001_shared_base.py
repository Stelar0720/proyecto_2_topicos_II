"""Esquema inicial congelado; no importar modelos cambiantes de la aplicación."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("spaces",
        sa.Column("code", sa.String(4), primary_key=True),
        sa.Column("category", sa.String(12), nullable=False),
        sa.CheckConstraint("category IN ('preferential','general')", name=op.f("ck_spaces_category")))
    op.create_table("allocation_guard", sa.Column("id", sa.Integer, primary_key=True),
                    sa.CheckConstraint("id = 1", name=op.f("ck_allocation_guard_singleton")))
    op.bulk_insert(sa.table("allocation_guard", sa.column("id", sa.Integer)), [{"id": 1}])
    op.create_table("staff",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("role", sa.String(12), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("username", name="uq_staff_username"),
        sa.CheckConstraint("role IN ('celador','vigilancia','admin')", name=op.f("ck_staff_role")))
    op.create_table("staff_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("staff_id", sa.String(36), sa.ForeignKey("staff.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("expires_at > created_at", name=op.f("ck_staff_sessions_expiration")))
    op.create_index("ix_staff_sessions_staff_id", "staff_sessions", ["staff_id"])
    op.create_table("reservations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plate", sa.String(12), nullable=False),
        sa.Column("space_id", sa.String(4), sa.ForeignKey("spaces.code"), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("token_hash", name="uq_reservations_token_hash"),
        sa.UniqueConstraint("id", "space_id", "plate", name="uq_reservation_identity"),
        sa.CheckConstraint("status IN ('pending','expired','cancelled','used')", name=op.f("ck_reservations_status")),
        sa.CheckConstraint("expires_at > created_at", name=op.f("ck_reservations_expiration")),
        sa.CheckConstraint("(status = 'cancelled' AND cancelled_at IS NOT NULL AND used_at IS NULL) OR "
                           "(status = 'used' AND used_at IS NOT NULL AND cancelled_at IS NULL) OR "
                           "(status IN ('pending','expired') AND cancelled_at IS NULL AND used_at IS NULL)",
                           name=op.f("ck_reservations_terminal_time")))
    op.create_index("uq_reservations_pending_plate", "reservations", ["plate"], unique=True,
                    sqlite_where=sa.text("status = 'pending'"), postgresql_where=sa.text("status = 'pending'"))
    op.create_table("stays",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plate", sa.String(12), nullable=False),
        sa.Column("space_id", sa.String(4), sa.ForeignKey("spaces.code"), nullable=False),
        sa.Column("reservation_id", sa.String(36), sa.ForeignKey("reservations.id")),
        sa.Column("ticket_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(6), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exited_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("reservation_id", name="uq_stays_reservation_id"),
        sa.UniqueConstraint("ticket_hash", name="uq_stays_ticket_hash"),
        sa.UniqueConstraint("id", "space_id", "plate", name="uq_stay_identity"),
        sa.CheckConstraint("status IN ('open','closed')", name=op.f("ck_stays_status")),
        sa.CheckConstraint("(status = 'open' AND exited_at IS NULL) OR "
                           "(status = 'closed' AND exited_at IS NOT NULL AND exited_at >= entered_at)",
                           name=op.f("ck_stays_exit_time")))
    for name, column in (("uq_stays_open_plate", "plate"), ("uq_stays_open_space", "space_id")):
        op.create_index(name, "stays", [column], unique=True,
                        sqlite_where=sa.text("status = 'open'"), postgresql_where=sa.text("status = 'open'"))
    op.create_table("allocations",
        sa.Column("space_id", sa.String(4), sa.ForeignKey("spaces.code"), primary_key=True),
        sa.Column("plate", sa.String(12), nullable=False),
        sa.Column("reservation_id", sa.String(36)),
        sa.Column("stay_id", sa.String(36)),
        sa.UniqueConstraint("plate", name="uq_allocations_plate"),
        sa.UniqueConstraint("reservation_id", name="uq_allocations_reservation_id"),
        sa.UniqueConstraint("stay_id", name="uq_allocations_stay_id"),
        sa.CheckConstraint("(reservation_id IS NOT NULL AND stay_id IS NULL) OR "
                           "(reservation_id IS NULL AND stay_id IS NOT NULL)", name=op.f("ck_allocations_one_source")),
        sa.ForeignKeyConstraint(["reservation_id", "space_id", "plate"],
                                ["reservations.id", "reservations.space_id", "reservations.plate"],
                                name="fk_allocation_reservation_identity"),
        sa.ForeignKeyConstraint(["stay_id", "space_id", "plate"],
                                ["stays.id", "stays.space_id", "stays.plate"],
                                name="fk_allocation_stay_identity"))
    op.create_table("payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("stay_id", sa.String(36), sa.ForeignKey("stays.id"), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("staff_id", sa.String(36), sa.ForeignKey("staff.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.UniqueConstraint("stay_id", name="uq_payments_stay_id"),
        sa.UniqueConstraint("idempotency_key", name="uq_payments_idempotency_key"),
        sa.CheckConstraint("amount_cents >= 0", name=op.f("ck_payments_nonnegative_amount")))


def downgrade():
    for table in ("payments", "allocations", "stays", "reservations", "staff_sessions",
                  "staff", "allocation_guard", "spaces"):
        op.drop_table(table)
