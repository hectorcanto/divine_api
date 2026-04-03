import asyncio
import logging
from logging.config import fileConfig
import os
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

import divine.devices.persistence.db_models  # noqa: F401
from divine.shared.persistence.db_base import Base
import divine.users.persistence.db_models  # noqa: F401


# pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
# with pyproject_path.open("rb") as f:
#    config_data = tomli.load(f)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
# config = config_data["tool"]["alembic"]
logger = logging.getLogger(__name__)

# NOTE this only works locally
ROOT_PATH = Path(__file__).parent.parent.parent
dotenv_path = ROOT_PATH / ".private" / "local.db.env"

load_dotenv(dotenv_path)

# TODO consider using pydantic setting to build url
host = os.getenv("DVN_DB_HOST", "")
port = int(os.getenv("DVN_DB_PORT", 5432))
user = os.getenv("DVN_DB_USER", "")
password = os.getenv("DVN_DB_PASSWORD", "")
name = os.getenv("DVN_DB_NAME", "")


config = context.config
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}",
)
print(f"Connecting to: postgresql+asyncpg://{user}:******@{host}:{port}/{name}")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    Uses a URL and no engine. Best for CI/CD or scripting.
    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = create_async_engine(
        url=config.get_main_option("sqlalchemy.url"),  # type: ignore
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:

        def do_run_migrations(the_connection) -> None:
            context.configure(
                connection=the_connection,
                target_metadata=target_metadata,
                # compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()

        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
