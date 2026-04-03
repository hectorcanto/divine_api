from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    SecretStr,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class OtelSection(BaseModel):
    host: str
    port: PositiveInt


class DbSection(BaseModel):
    host: str
    port: int = Field(default=5432)
    user: str
    password: SecretStr
    name: str
    commit: bool = Field(default=True)

    @property
    def url(self):
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
            password=self.password.get_secret_value(),
            **self.model_dump(exclude={"password"}),
        )


class AppSettings(BaseSettings):  # type: ignore[reportArgumentType]
    model_config = SettingsConfigDict(env_prefix="DVN_", env_nested_delimiter="_", env_nested_max_split=1)
    log_level: str = "INFO"
    app_name: str = "Divine"
    env_purpose: str
    env_stage: str
    db: DbSection = Field(default_factory=DbSection)  # type:ignore
    otel: OtelSection


def get_settings():
    return AppSettings()  # type: ignore
