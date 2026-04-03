from abc import (
    ABC,
    abstractmethod,
)

from divine.users.interface.schemas import UserCreateSchema

from .entities import (
    User,
    UserId,
)


class BaseUserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def list(self) -> list[User]: ...

    # @abstractmethod
    # def update(self, user_id: UserId, user: UserNullable) -> User: ...

    @abstractmethod
    async def delete(self, user_id: UserId) -> None: ...

    @abstractmethod
    async def insert(self, user_schema: UserCreateSchema) -> User: ...
