from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from .devices.interface.views import devices_router
from .extensions.observability_extensions import setup_tracing
from .extensions.python_extensions import get_version
from .settings import get_settings
from .shared.persistence.db_orm import PostgresDB
from .users.interface.views import users_router


logger = logging.getLogger("divine.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")

    database = PostgresDB(app.state.settings.db.url, commit=app.state.settings.db.commit)
    app.state.database = database
    settings = app.state.settings
    if settings.env_purpose != "SKIP":  # use "TESTS" to disable in tests if necessary
        setup_tracing(
            app,
            app.state.database._engine,
            host=settings.otel.host,
            port=settings.otel.port,
            app_name=settings.app_name,
        )
    logger.info(f"Init DB Engine for {database}")
    yield
    await app.state.database.dispose_engine()


def create_app(commit: bool = True):
    """Create app with a factory, compatible with uvicorn

    Create another function for testing purpose if needed, with disabled services like observability
    """

    settings = get_settings()
    effective_log_level = logging.getLevelNamesMapping()[settings.log_level]
    # TODO move to a setup_logging util
    logging.basicConfig(
        level=effective_log_level,
        format="%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    for logger_name in [
        "asyncio",
        "httpx",
    ]:
        logging.getLogger(logger_name).setLevel(max(logging.WARNING, effective_log_level))

    app_version = get_version()
    the_app = FastAPI(
        title=settings.app_name,
        version=app_version,
        debug=False,
        lifespan=lifespan,
        # exception_handlers
    )
    the_app.state.settings = settings

    # the_app.add_middleware(
    # AuthenticationMiddleware,
    # backend=BasicAuth(),
    # on_error=on_authentication_error,
    # )
    the_app.include_router(users_router, tags=["users"])
    the_app.include_router(devices_router, tags=["devices"])
    return the_app
