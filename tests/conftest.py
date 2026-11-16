import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from plaza_reserva.config import Settings
from plaza_reserva.db import build_engine
from plaza_reserva.main import create_app


class FrozenClock:
    def __init__(self):
        self.value = datetime(2026, 11, 15, 17, 0, tzinfo=UTC)

    def now(self):
        return self.value


@pytest.fixture
def clock():
    return FrozenClock()


@pytest.fixture(params=["sqlite"] + (["postgresql"] if os.getenv("TEST_POSTGRES_URL") else []))
def engine(request, tmp_path):
    admin = None
    schema = None
    if request.param == "sqlite":
        engine = build_engine(f"sqlite:///{(tmp_path / 'base.db').as_posix()}")
    else:
        url = make_url(os.environ["TEST_POSTGRES_URL"])
        if not url.database or not url.database.endswith("_test"):
            pytest.fail("TEST_POSTGRES_URL debe apuntar a una BD descartable terminada en _test")
        schema = "test_" + uuid4().hex
        admin = create_engine(url)
        with admin.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    config = Config("alembic.ini")
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    yield engine
    engine.dispose()
    if admin:
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def client(engine, clock):
    settings = Settings(app_env="test")
    with TestClient(create_app(settings, clock, engine)) as client:
        yield client
