"""Integration test fixtures using testcontainers for DB"""

import asyncio
from collections.abc import (
    AsyncGenerator,
    AsyncIterator,
    Iterator,
)
import logging
import os
import random
import uuid

from alembic import command
from alembic.config import Config
from httpx import (
    ASGITransport,
    AsyncClient,
    BasicAuth,
)
from polyfactory.factories.sqlalchemy_factory import (
    SQLAASyncPersistence,
    SQLAlchemyFactory,
    SQLAlchemyPersistenceMethod,
)
import pytest
import pytest_asyncio
from sqlalchemy import (
    delete,
    make_url,
    pool,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from divine import app_factory
from divine.dependencies import get_session
from divine.users.domain.entities import UserId
from divine.users.persistence.db_models import DbUser

from tests.utils import (
    PROJECT_ROOT,
)


logger = logging.getLogger(__name__)

# Alembic configuration

alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "src" / "migrations"))
POSTGRES_IMAGE = "postgres:18-alpine"
_USER_EMAIL = "supercow@milk.com"
_SECOND_USER = "less.important@test.com"

_USER_PASSWORD = "m1lk_1s_l1f3"


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the whole test session."""

    # policy = get_event_loop_policy(), before python3.14
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", name="db_container")
def db_container_fx(event_loop, test_settings) -> Iterator[PostgresContainer]:
    """Start a Postgres container for the test session."""
    in_ci = os.getenv("DVN_ENV_STAGE", "NOT_CI") == "CI"
    fixed_db_port = os.getenv("TEST_DB_PORT") if not in_ci else None
    port = fixed_db_port or random.randint(49152, 65535)  # noqa: S311

    image = POSTGRES_IMAGE.replace(":", "-")
    random_suffix = uuid.uuid4().hex[:8]
    container_name = f"divine-db-{image}-{random_suffix}"

    with (
        PostgresContainer(
            image=POSTGRES_IMAGE,
            dbname=test_settings.db.name,
            username=test_settings.db.user,
            password=test_settings.db.password.get_secret_value(),
        )
        .with_name(container_name)
        .with_bind_ports(5432, int(port)) as container
    ):
        logger.info(f"Creating testcontainer DB '{test_settings.db.name}' exposed in port {port}")

        sync_url = container.get_connection_url()  # plain postgresql://
        alembic_cfg.set_section_option("alembic", "sqlalchemy.url", sync_url)
        command.upgrade(alembic_cfg, "head")  # TODO(h): reuse migrations
        yield container


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_engine(db_container: PostgresContainer, event_loop) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        url=make_url(db_container.get_connection_url()).set(drivername="postgresql+asyncpg"),
        poolclass=pool.NullPool,
    )
    # create_all not needed with alembic migrations plugin
    # async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)
    yield engine
    # async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session", scope="session", name="auth_user", autouse=True)
async def auth_user_fx(db_engine: AsyncEngine) -> AsyncIterator[UserId]:
    """Creates a default user available for the entire test session."""
    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        user = DbUser(
            email=_USER_EMAIL,
            first_name="Super",
            last_name="Cow",
            password=_USER_PASSWORD,
        )
        session.add(user)

        await session.commit()
        user_id = user.id

    yield user_id

    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        await session.execute(delete(DbUser).where(DbUser.email == _USER_EMAIL))
        await session.commit()


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def another_user(db_engine) -> AsyncIterator[UserId]:
    """Creates a default user available for the entire test session."""
    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        user = DbUser(
            email=_SECOND_USER,
            first_name="Less",
            last_name="Important",
            password="anything",
        )
        session.add(user)

        await session.commit()
        user_id = user.id

    yield user_id

    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        await session.execute(delete(DbUser).where(DbUser.email == _USER_EMAIL))
        await session.commit()


# async_session might not be session scoped fixture, but if you can work with existing fixture without deleting them, it will be faster.
@pytest_asyncio.fixture(loop_scope="function", name="test_db_session")
async def test_db_session_fx(db_engine) -> AsyncGenerator[AsyncSession]:
    """Creates an async session for tests."""

    async with AsyncSession(db_engine, expire_on_commit=False, autoflush=False) as session:
        SQLAlchemyFactory.__async_persistence__ = SQLAASyncPersistence(  # type: ignore[reportGeneralTypeIssues]
            session,
            persistence_method=SQLAlchemyPersistenceMethod.FLUSH,
        )
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()  # implicit rollback
        # Removes all rows to have empty tables for the next tests
        # await session.execute(delete(DbDeviceProfile))
        # Truncate "autoincrement" counters (if necessary)
        # await session.execute(text('TRUNCATE TABLE "users" RESTART IDENTITY CASCADE'))
        # await session.execute(text('TRUNCATE TABLE "devices" RESTART IDENTITY CASCADE'))


@pytest_asyncio.fixture(loop_scope="function", name="integration_client")
async def integration_client_fx(auth_user, test_db_session) -> AsyncGenerator[AsyncClient]:
    app = app_factory.create_app()

    # override get_session so the app uses the test transaction
    def override_get_session():
        try:
            yield test_db_session
        finally:
            pass  # rollback is handled by the test_db_session fixture

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        auth=BasicAuth(_USER_EMAIL, _USER_PASSWORD),
    ) as client:
        yield client

    app.dependency_overrides.clear()
