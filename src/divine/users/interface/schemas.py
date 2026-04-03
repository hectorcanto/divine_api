from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
)


class UserCreateSchema(BaseModel):
    email: EmailStr
    first_name: str = Field(examples=["John"])
    last_name: str = Field(examples=["Smith"])
    password: SecretStr = Field(examples=["dont_use_admin"])


class UserPatchSchema(BaseModel):
    first_name: str | None
    last_name: str | None
