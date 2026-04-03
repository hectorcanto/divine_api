from typing import (
    Annotated,
    Any,
)

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    model_validator,
)

from ..domain.entities import (
    DeviceFromTemplateDTO,
    DeviceProfileDTO,
    DeviceTemplateDTO,
    DeviceTemplateId,
    DeviceType,
)
from .validators import validate_numeric_country_code


MIN_PHONE_PX = 320
MAX_8K_PX = 7680

CountryCode = Annotated[int, AfterValidator(validate_numeric_country_code)]
PixelSize = Annotated[int, Field(ge=MIN_PHONE_PX, le=MAX_8K_PX)]


class WindowSize(BaseModel):
    width: PixelSize
    height: PixelSize


class DeviceCreateSchema(BaseModel):
    device_type: DeviceType
    size: WindowSize
    user_agent: str = Field(examples=["Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)"])
    headers: dict[str, Any] = Field(examples=[{}])
    country_code: CountryCode | None = Field(examples=[826, 250])

    def to_dto(self) -> DeviceProfileDTO:
        return DeviceProfileDTO(
            **self.model_dump(exclude={"size"}),
            width=self.size.width,
            height=self.size.height,
        )


class TemplateCreateSchema(BaseModel):
    name: str = Field(examples=["Custom template #1"])
    device_type: DeviceType
    size: WindowSize
    user_agent: str = Field(examples=["Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)"])

    def to_dto(self) -> DeviceTemplateDTO:
        return DeviceTemplateDTO(
            name=self.name,
            device_type=self.device_type,
            width=self.size.width,
            height=self.size.height,
            user_agent=self.user_agent,
        )


class DeviceCreateFromTemplateSchema(BaseModel):
    template_id: DeviceTemplateId = Field(examples=[2])
    headers: dict[str, Any]
    country_code: CountryCode = Field(examples=[724])

    def to_dto(self) -> DeviceFromTemplateDTO:
        return DeviceFromTemplateDTO(**self.model_dump())


class DevicePatchSchema(BaseModel):
    device_type: DeviceType | None = None
    size: WindowSize | None = None
    user_agent: str | None = None
    country_code: CountryCode | None = None
    headers: dict[str, Any] | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "DevicePatchSchema":
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one field must be provided")
        return self
