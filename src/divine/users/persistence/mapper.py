from ..domain.entities import User
from ..interface.schemas import UserCreateSchema
from .db_models import DbUser


class UserMapper:
    @staticmethod
    def to_entity(row: DbUser) -> User:
        return User.from_attributes_without_validation(row)

    @staticmethod
    def to_row(user: UserCreateSchema) -> DbUser:
        return DbUser(
            **user.model_dump(exclude={"password"}),
            password=user.password.get_secret_value(),
        )
