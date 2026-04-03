from collections.abc import AsyncGenerator

from fastapi import (
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from divine.devices.domain.repository_interface import BaseDeviceRepository
from divine.devices.persistence.postgres_repository import PostgresDeviceProfileRepository
from divine.users.domain.repository_interface import BaseUserRepository
from divine.users.persistence.postgres_repository import PostgresUserRepository


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    sessionmaker = request.app.state.database.session_maker
    if not sessionmaker:
        raise RuntimeError("Database engine not initialized")
    async with sessionmaker() as session:
        yield session
        await session.commit()


def inject_user_repo(session: AsyncSession = Depends(get_session)) -> BaseUserRepository:
    return PostgresUserRepository(session)


def inject_device_repo(session: AsyncSession = Depends(get_session)) -> BaseDeviceRepository:
    return PostgresDeviceProfileRepository(session)
