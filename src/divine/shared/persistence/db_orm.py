from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.sql import text


logger = logging.getLogger(__name__)


class PostgresDB:
    def __init__(self, db_url: str, echo: bool = False, commit: bool = True):
        self.url = db_url
        # TODO consider adding host, port, and name for logging purposes
        self.commit = commit
        self._engine = create_async_engine(
            url=db_url,
            pool_size=5,
            pool_use_lifo=False,
            pool_timeout=5,
            echo=echo,
            # json_serializer=serializer,
            future=True,
        )

        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,  # NOTE very relevant for inconsistencies
            autoflush=True,
        )
        self._make_session_no_flush = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @property
    def sessionmaker_no_flush(self) -> async_sessionmaker[AsyncSession]:
        """shortcut for session/transaction creation"""
        return self._make_session_no_flush

    async def dispose_engine(self):
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def test_connection(self) -> bool:
        """Quick test connection for DB"""
        async with self.session_maker() as session:
            await session.execute(text("SELECT 1"))
        logger.debug("Connection to DB OK")
        return True

    @asynccontextmanager
    async def start(self) -> AsyncIterator[AsyncSession]:
        """Start transaction with async context manager. Currently unused"""
        async with self.session_maker() as session:
            async with session.begin():
                try:
                    yield session
                    if self.commit:
                        await session.commit()
                except:
                    await session.rollback()
                    raise
