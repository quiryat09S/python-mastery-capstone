import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context
from labs.final_orders.infrastructure.models import Base

PROJECT_ROOT = Path(__file__).resolve().parents[5]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


config = context.config

database_url_from_env = os.getenv("DATABASE_URL")  # type: ignore[arg-type]

if database_url_from_env is None:
    database_url_from_config = config.get_main_option("sqlalchemy.url")
else:
    database_url_from_config = database_url_from_env

if database_url_from_config is None:
    raise RuntimeError("No se configuró la URL de la base de datos")

database_url = str(database_url_from_config)

config.set_main_option(
    "sqlalchemy.url",
    database_url,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
