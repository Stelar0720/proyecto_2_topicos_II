"""Contrato compartido. Cambios coordinados con Jack y migración sucesora."""
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint,
    Index, Integer, MetaData, String, UniqueConstraint, text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Se requiere un instante con zona horaria")
        value = value.astimezone(UTC)
        return value.replace(tzinfo=None) if dialect.name == "sqlite" else value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


def new_id() -> str:
    return str(uuid4())


class Space(Base):
    __tablename__ = "spaces"
    code: Mapped[str] = mapped_column(String(4), primary_key=True)
    category: Mapped[str] = mapped_column(String(12))
    __table_args__ = (CheckConstraint("category IN ('preferential','general')", name="category"),)


class AllocationGuard(Base):
    __tablename__ = "allocation_guard"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    __table_args__ = (CheckConstraint("id = 1", name="singleton"),)


class Staff(Base):
    __tablename__ = "staff"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(12))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime())
    __table_args__ = (CheckConstraint("role IN ('admin','client')", name="role"),)


class StaffSession(Base):
    __tablename__ = "staff_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    staff_id: Mapped[str] = mapped_column(ForeignKey("staff.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime())
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    __table_args__ = (CheckConstraint("expires_at > created_at", name="expiration"),)


class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    plate: Mapped[str] = mapped_column(String(12))
    customer_name: Mapped[str | None] = mapped_column(String(80))
    space_id: Mapped[str] = mapped_column(ForeignKey("spaces.code"))
    status: Mapped[str] = mapped_column(String(10))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_code: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime())
    scheduled_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    cancelled_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    __table_args__ = (
        UniqueConstraint("id", "space_id", "plate", name="uq_reservation_identity"),
        CheckConstraint("status IN ('pending','expired','cancelled','used')", name="status"),
        CheckConstraint("scheduled_at IS NULL OR expires_at > scheduled_at", name="expiration"),
        CheckConstraint("(status = 'cancelled' AND cancelled_at IS NOT NULL AND used_at IS NULL) OR "
                        "(status = 'used' AND used_at IS NOT NULL AND cancelled_at IS NULL) OR "
                        "(status IN ('pending','expired') AND cancelled_at IS NULL AND used_at IS NULL)", name="terminal_time"),
        Index("uq_reservations_pending_plate", "plate", unique=True,
              sqlite_where=text("status = 'pending'"), postgresql_where=text("status = 'pending'")),
    )


class Stay(Base):
    __tablename__ = "stays"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    plate: Mapped[str] = mapped_column(String(12))
    space_id: Mapped[str] = mapped_column(ForeignKey("spaces.code"))
    reservation_id: Mapped[str | None] = mapped_column(ForeignKey("reservations.id"), unique=True)
    ticket_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_code: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(6))
    entered_at: Mapped[datetime] = mapped_column(UTCDateTime())
    exited_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    __table_args__ = (
        UniqueConstraint("id", "space_id", "plate", name="uq_stay_identity"),
        CheckConstraint("status IN ('open','closed')", name="status"),
        CheckConstraint("(status = 'open' AND exited_at IS NULL) OR "
                        "(status = 'closed' AND exited_at IS NOT NULL AND exited_at >= entered_at)", name="exit_time"),
        Index("uq_stays_open_plate", "plate", unique=True,
              sqlite_where=text("status = 'open'"), postgresql_where=text("status = 'open'")),
        Index("uq_stays_open_space", "space_id", unique=True,
              sqlite_where=text("status = 'open'"), postgresql_where=text("status = 'open'")),
    )


class Allocation(Base):
    __tablename__ = "allocations"
    space_id: Mapped[str] = mapped_column(ForeignKey("spaces.code"), primary_key=True)
    plate: Mapped[str] = mapped_column(String(12), unique=True)
    reservation_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    stay_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    __table_args__ = (
        CheckConstraint("(reservation_id IS NOT NULL AND stay_id IS NULL) OR "
                        "(reservation_id IS NULL AND stay_id IS NOT NULL)", name="one_source"),
        ForeignKeyConstraint(["reservation_id", "space_id", "plate"],
                             ["reservations.id", "reservations.space_id", "reservations.plate"],
                             name="fk_allocation_reservation_identity"),
        ForeignKeyConstraint(["stay_id", "space_id", "plate"],
                             ["stays.id", "stays.space_id", "stays.plate"], name="fk_allocation_stay_identity"),
    )


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    stay_id: Mapped[str] = mapped_column(ForeignKey("stays.id"), unique=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    paid_at: Mapped[datetime] = mapped_column(UTCDateTime())
    staff_id: Mapped[str] = mapped_column(ForeignKey("staff.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    __table_args__ = (CheckConstraint("amount_cents >= 0", name="nonnegative_amount"),)
