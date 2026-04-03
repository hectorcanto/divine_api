from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from divine.dependencies import get_session
from divine.users.persistence.db_models import DbUser


security = HTTPBasic()


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> DbUser:
    user = (await session.scalars(select(DbUser).where(DbUser.email == credentials.username))).one_or_none()

    if not user or not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user
