from alembic import context

from plaza_reserva.config import Settings
from plaza_reserva.db import build_engine
from plaza_reserva.models import Base

config = context.config


def migrate(connection):
    context.configure(connection=connection, target_metadata=Base.metadata,
                      compare_type=True, render_as_batch=connection.dialect.name == "sqlite")
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=Settings.from_env().database_url, target_metadata=Base.metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()
else:
    supplied = config.attributes.get("connection")
    if supplied is not None:
        migrate(supplied)
    else:
        engine = build_engine(Settings.from_env().database_url)
        with engine.connect() as connection:
            migrate(connection)
        engine.dispose()
