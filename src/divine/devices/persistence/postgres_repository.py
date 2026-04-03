import dataclasses
from datetime import (
    datetime,
    UTC,
)
import logging
from typing import cast

from sqlalchemy import (
    CursorResult,
    delete as sqlalchemy_delete,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from divine.users.domain.entities import UserId

from ..domain.entities import (
    DeviceFromTemplateDTO,
    DeviceId,
    DeviceProfile,
    DeviceProfileDTO,
    DeviceProfileNullableDTO,
    DeviceTemplate,
    DeviceTemplateDTO,
    DeviceTemplateId,
)
from ..domain.exceptions import (
    DeviceProfileNotFoundError,
    DeviceTemplateNotFoundError,
    TemplateNameAlreadyExistsError,
)
from ..domain.repository_interface import BaseDeviceRepository
from .db_models import (
    DbDeviceProfile,
    DbDeviceTemplate,
)
from .mapper import (
    DeviceProfileMapper,
    DeviceTemplateMapper,
)


logger = logging.getLogger(__name__)


class PostgresDeviceProfileRepository(BaseDeviceRepository):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _find_by_id_raw(self, user_id: UserId, device_id: DeviceId) -> DbDeviceProfile | None:
        return (
            await self.session.scalars(
                select(DbDeviceProfile).where(
                    DbDeviceProfile.user_id == user_id,
                    DbDeviceProfile.id == device_id,
                    DbDeviceProfile.deleted_at.is_(None),
                )
            )
        ).one_or_none()

    async def find_by_id(self, user_id: UserId, device_id: DeviceId) -> DeviceProfile | None:
        row = await self._find_by_id_raw(user_id, device_id)
        return DeviceProfileMapper.to_entity(row) if row else None

    async def list(self, user_id: UserId) -> list[DeviceProfile]:
        device_list = (
            await self.session.scalars(
                select(DbDeviceProfile).where(
                    DbDeviceProfile.user_id == user_id,
                    DbDeviceProfile.deleted_at.is_(None),
                )
            )
        ).all()
        # TODO(h): implement limit and offset
        return [DeviceProfileMapper.to_entity(item) for item in device_list]

    async def insert(self, user_id: UserId, device_profile: DeviceProfileDTO) -> DeviceProfile:
        row = DeviceProfileMapper.to_row(user_id, device_profile)
        self.session.add(row)
        await self.session.flush()
        return DeviceProfileMapper.to_entity(row)

    async def insert_from_template(self, user_id: UserId, dto: DeviceFromTemplateDTO) -> DeviceProfile:
        template = await self._find_template_by_id(dto.template_id)
        if not template:
            raise DeviceTemplateNotFoundError(f"Template with id {dto.template_id} not found")

        row = DeviceProfileMapper.to_row_from_template(user_id, template, dto)
        self.session.add(row)
        await self.session.flush()
        return DeviceProfileMapper.to_entity(row)

    async def update(self, user_id: UserId, device_profile: DeviceProfileNullableDTO) -> DeviceProfile:
        row = await self._find_by_id_raw(user_id, device_profile.id)
        if not row:
            raise DeviceProfileNotFoundError(device_profile.id)

        for field, value in dataclasses.asdict(device_profile).items():
            if field == "id":
                continue
            if value is not None:
                setattr(row, field, value)
        await self.session.flush()
        return DeviceProfileMapper.to_entity(row)

    async def delete(self, user_id: UserId, device_id: DeviceId) -> bool:
        result = cast(
            CursorResult,
            await self.session.execute(
                sqlalchemy_delete(DbDeviceProfile).where(
                    DbDeviceProfile.user_id == user_id, DbDeviceProfile.id == device_id
                )
            ),
        )
        if result.rowcount == 0:
            return False
        await self.session.flush()
        return True

    async def soft_delete(self, user_id: UserId, device_id: DeviceId) -> bool:
        delete_dto = DeviceProfileNullableDTO(id=device_id, deleted_at=datetime.now(tz=UTC))
        try:
            await self.update(user_id, delete_dto)
        except DeviceProfileNotFoundError:
            return False
        return True

    # TEMPLATES
    async def insert_template(self, dto: DeviceTemplateDTO) -> DeviceTemplate:
        row = DeviceTemplateMapper.to_row(dto)
        logger.debug(row.__dict__)
        try:
            self.session.add(row)
            await self.session.flush()
        except IntegrityError:  # UniqueViolationError:
            await self.session.rollback()
            raise TemplateNameAlreadyExistsError(f"Name {dto.name} is already taken for a template")
        except Exception as exc:
            await self.session.rollback()
            error_msg = "Unexpected exception while inserting template"
            logger.warning(error_msg, exc_info=True)
            # TODO(h): add global exception handler to return a nice 500
            raise Exception(error_msg) from exc
        return DeviceTemplateMapper.to_entity(row)

    async def list_templates(self) -> list[DeviceTemplate]:
        template_list = (await self.session.scalars(select(DbDeviceTemplate))).all()
        return [DeviceTemplateMapper.to_entity(item) for item in template_list]

    async def _find_template_by_id(self, template_id: DeviceTemplateId) -> DbDeviceTemplate | None:
        row = (
            await self.session.scalars(select(DbDeviceTemplate).where(DbDeviceTemplate.id == template_id))
        ).one_or_none()
        return row
