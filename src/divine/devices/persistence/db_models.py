from datetime import (
    datetime,
)
from enum import IntEnum
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from divine.devices.domain.entities import (
    DeviceId,
    DeviceTemplateId,
)
from divine.extensions.db_extensions import (
    ReprMixin,
    TimedMixin,
)
from divine.shared.persistence.db_base import Base
from divine.users.domain.entities import UserId


class DbDeviceType(IntEnum):
    Desktop = 1
    Mobile = 2


class DbDeviceProfile(ReprMixin, Base, TimedMixin):
    """Basic device profile"""

    __tablename__ = "devices_profiles"  # TODO(h): rename to device_profiles

    # I prefer integer for simplicity, an UUID could be used as public id
    id: Mapped[DeviceId] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UserId] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    template_id: Mapped[DeviceTemplateId] = mapped_column(
        Integer, ForeignKey("device_templates.id"), nullable=True, index=True, default=None
    )
    device_type: Mapped[DbDeviceType] = mapped_column(SmallInteger, nullable=False)
    # TODO mapped_column(SAEnum(DbDeviceType, native_enum=False), nullable=False)

    width: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    height: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # 300 covers larger mobile user agent string, but some margin is nice
    user_agent: Mapped[str] = mapped_column(String(1000), nullable=False)
    country_code: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # ISO 3166-1 alpha-2 numeric
    headers: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)


class DbDeviceTemplate(ReprMixin, Base):
    __tablename__ = "device_templates"

    id: Mapped[DeviceTemplateId] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    device_type: Mapped[DbDeviceType] = mapped_column(SmallInteger, nullable=False)
    width: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    height: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    user_agent: Mapped[str] = mapped_column(String(1000), nullable=False)
