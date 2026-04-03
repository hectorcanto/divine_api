from dataclasses import dataclass
from datetime import (
    datetime,
)
from typing import (
    NewType,
)

from pydantic import (
    ConfigDict,
    EmailStr,
    Field,
)

from divine.extensions.domain_extensions import ExtendedBaseModel


UserId = NewType("UserId", int)


class User(ExtendedBaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UserId
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = Field(default=None, exclude=True)


@dataclass(frozen=True)
class UserNullableDTO:
    """For patching"""

    first_name: str | None = None
    last_name: str | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
