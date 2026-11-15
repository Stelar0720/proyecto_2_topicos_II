from contextlib import contextmanager
from pathlib import Path

from fastapi import Request
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from .models import AllocationGuard


def build_engine(database_url: str):
    url = make_url(database_url)
    if url.get_backend_name() not in {"sqlite", "postgresql"}:
        raise ValueError("Solo SQLite y PostgreSQL están previstos")
    kwargs = {"pool_pre_ping": True}
    if url.get_backend_name() == "sqlite":
        if url.database and url.database != ":memory:":
            Path(url.database).resolve().parent.mkdir(parents=True, exist_ok=True)
        kwargs["connect_args"] = {"check_same_thread": False, "timeout": 5}
    engine = create_engine(url, **kwargs)
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def configure_sqlite(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA busy_timeout=5000")
    return engine


def get_session(request: Request):
    with Session(request.app.state.engine) as session:
        yield session


@contextmanager
def allocation_transaction(session: Session):
    """Primitiva compartida; no implementa asignaciones ni vencimientos.

    Usar sesión nueva SIN transacción previa; normalizar vencidas en el servicio.
    """
    if session.in_transaction():
        raise RuntimeError("La asignación requiere sesión nueva sin lecturas previas")
    with session.begin():
        if session.get_bind().dialect.name == "sqlite":
            session.execute(text("BEGIN IMMEDIATE"))
        guard = session.scalar(select(AllocationGuard).where(
            AllocationGuard.id == 1
        ).with_for_update())
        if guard is None:
            raise RuntimeError("Falta migración inicial: allocation_guard")
        yield session
