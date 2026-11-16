from datetime import timedelta

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from plaza_reserva.cli import seed_spaces
from plaza_reserva.db import allocation_transaction
from plaza_reserva.models import Allocation, Base, Reservation, Space
from plaza_reserva.security import new_token, token_digest


def test_database_rejects_duplicate_pending_plate(engine, clock):
    with Session(engine) as session:
        seed_spaces(session)
        for code in ("P001", "P002"):
            session.add(Reservation(plate="TEST01", space_id=code, status="pending",
                                    token_hash=token_digest(new_token()), created_at=clock.now(),
                                    expires_at=clock.now()+timedelta(minutes=30)))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        assert session.scalar(select(Reservation)) is None


def test_allocation_requires_matching_identity(engine, clock):
    with Session(engine) as session:
        seed_spaces(session)
        with allocation_transaction(session):
            r = Reservation(plate="TEST02", space_id="P001", status="pending",
                            token_hash=token_digest(new_token()), created_at=clock.now(),
                            expires_at=clock.now()+timedelta(minutes=30))
            session.add(r)
            session.flush()
            reservation_id = r.id
        with pytest.raises(IntegrityError):
            with allocation_transaction(session):
                session.add(Allocation(space_id="P002", plate="OTRA02", reservation_id=reservation_id))


def test_allocation_transaction_rolls_back(engine):
    with Session(engine) as session:
        with pytest.raises(ValueError):
            with allocation_transaction(session):
                session.add(Space(code="G001", category="general"))
                session.flush()
                raise ValueError("fallo simulado")
        assert session.get(Space, "G001") is None


def test_migration_matches_models_and_downgrades(engine):
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        assert compare_metadata(context, Base.metadata) == []
    config = Config("alembic.ini")
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) <= {"alembic_version"}
