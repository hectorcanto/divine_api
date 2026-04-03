import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from divine.dependencies import (
    inject_user_repo,
)
from divine.users.domain.exceptions import UserEmailAlreadyExist
from divine.users.persistence.postgres_repository import PostgresUserRepository

from ..domain.entities import User
from ..domain.repository_interface import BaseUserRepository
from .schemas import (
    UserCreateSchema,
)


# from starlette.authentication import requires


USER_RESOURCE = "/users"
logger = logging.getLogger(__name__)
users_router = APIRouter(prefix=USER_RESOURCE)


# NOTE for simplicity this endpoint is not authenticated, but it should be limited to admins
@users_router.post("", status_code=status.HTTP_201_CREATED, response_model=User, responses={409: {}})
async def create_user(
    user: UserCreateSchema,
    repository: PostgresUserRepository | BaseUserRepository = Depends(inject_user_repo),
):
    try:
        new_user = await repository.insert(user)
    except UserEmailAlreadyExist:
        raise HTTPException(status.HTTP_409_CONFLICT)
    return new_user
