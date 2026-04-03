from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import (
    Any,
    NewType,
)

from pydantic import (
    Field,
    PositiveInt,
)

from divine.extensions.domain_extensions import ExtendedBaseModel


DeviceId = NewType("DeviceId", int)
DeviceTemplateId = NewType("DeviceTemplateId", int)


class DeviceType(StrEnum):
    Desktop = "Desktop"
    Mobile = "Mobile"


class DeviceProfile(ExtendedBaseModel):
    id: DeviceId
    device_type: DeviceType
    width: PositiveInt = Field(examples=[1280])
    height: PositiveInt = Field(examples=[720])
    user_agent: str
    country_code: PositiveInt  # = Field(examples=[724], description="A numeric ISO country-code")
    headers: dict[str, Any] = Field(examples=[{"locale": "gl-ES"}])


class DeviceTemplate(ExtendedBaseModel):
    id: DeviceTemplateId
    name: str
    device_type: DeviceType
    width: PositiveInt = Field(examples=[1280])
    height: PositiveInt = Field(examples=[720])
    user_agent: str


@dataclass(frozen=True, slots=True)
class DeviceProfileDTO:
    """Transport object for new devices"""

    device_type: DeviceType
    width: PositiveInt
    height: PositiveInt
    user_agent: str
    country_code: PositiveInt
    headers: dict[str, Any]
    template_id: DeviceTemplateId | None = None


@dataclass(frozen=True, slots=True)
class DeviceProfileNullableDTO:
    """Transport object for patching devices"""

    id: DeviceId
    device_type: DeviceType | None = None
    width: PositiveInt | None = None
    height: PositiveInt | None = None
    user_agent: str | None = None
    country_code: PositiveInt | None = None
    headers: dict[str, Any] | None = None
    deleted_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class DeviceFromTemplateDTO:
    """Transport object for creating devices from templates"""

    template_id: DeviceTemplateId
    country_code: PositiveInt
    headers: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class DeviceTemplateDTO:
    """Transport object for patching devices"""

    name: str
    device_type: DeviceType
    width: PositiveInt
    height: PositiveInt
    user_agent: str
