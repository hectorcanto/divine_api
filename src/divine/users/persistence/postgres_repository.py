import logging
from typing import cast

from sqlalchemy import (
    CursorResult,
    delete as sqlalchemy_delete,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from divine.users.interface.schemas import UserCreateSchema

from ..domain.entities import (
    User,
    UserId,
)
from ..domain.exceptions import UserEmailAlreadyExist
from ..domain.repository_interface import BaseUserRepository
from .db_models import DbUser
from .mapper import UserMapper


logger = logging.getLogger(__name__)


class PostgresUserRepository(BaseUserRepository):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, user_id: UserId) -> User | None:
        """Select a user by id"""
        db_user = await self.session.get(DbUser, user_id)
        if not db_user:
            return None
        return UserMapper.to_entity(db_user)

    async def list(self) -> list[User]:
        result = await self.session.execute(select(DbUser))
        user_list = result.scalars().all()
        return [UserMapper.to_entity(item) for item in user_list]

    async def insert(self, user_schema: UserCreateSchema) -> User:
        """Inserts a new user

        Raises:
            IntegrityError if user email is in use
        """
        new_db_user = UserMapper.to_row(user_schema)

        self.session.add(new_db_user)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise UserEmailAlreadyExist(f"User with email {user_schema.email} already exists")
        return UserMapper.to_entity(new_db_user)

    async def delete(self, user_id: UserId) -> None:
        result: CursorResult = cast(
            CursorResult, await self.session.execute(sqlalchemy_delete(DbUser).where(DbUser.id == user_id))
        )
        if result.rowcount == 0:
            logger.warning("User was already deleted or it did not exist")
            # raise UserNotFoundError(user_id)
        await self.session.flush()
