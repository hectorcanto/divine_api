from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase

from divine.devices.domain.entities import (
    DeviceId,
    DeviceTemplateId,
)
from divine.users.domain.entities import UserId


class Base(DeclarativeBase):
    type_annotation_map = {
        UserId: Integer,
        DeviceId: Integer,
        DeviceTemplateId: Integer,
    }
