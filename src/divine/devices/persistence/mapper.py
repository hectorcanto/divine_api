from divine.users.domain.entities import UserId

from ..domain.entities import (
    DeviceFromTemplateDTO,
    DeviceProfile,
    DeviceProfileDTO,
    DeviceTemplate,
    DeviceTemplateDTO,
    DeviceType,
)
from .db_models import (
    DbDeviceProfile,
    DbDeviceTemplate,
    DbDeviceType,
)


class DeviceProfileMapper:
    @staticmethod
    def to_entity(row: DbDeviceProfile) -> DeviceProfile:

        entity = DeviceProfile.from_attributes_without_validation(row)
        # TODO(h): fix the resolution of DbEnum and StrEnum
        entity.device_type = DeviceType.Mobile if row.device_type == 2 else DeviceType.Desktop
        return entity

    @staticmethod
    def to_row(user_id: UserId, device_profile: DeviceProfileDTO) -> DbDeviceProfile:
        return DbDeviceProfile(
            user_id=user_id,
            device_type=DbDeviceType[device_profile.device_type],
            width=device_profile.width,
            height=device_profile.height,
            user_agent=device_profile.user_agent,
            country_code=device_profile.country_code,
            headers=device_profile.headers,
            template_id=device_profile.template_id,
        )

    @staticmethod
    def to_row_from_template(
        user_id: UserId, template: DbDeviceTemplate, dto: DeviceFromTemplateDTO
    ) -> DbDeviceProfile:
        return DbDeviceProfile(
            user_id=user_id,
            template_id=dto.template_id,
            device_type=template.device_type,
            width=template.width,
            height=template.height,
            user_agent=template.user_agent,
            country_code=dto.country_code,
            headers=dto.headers,
        )


class DeviceTemplateMapper:
    @staticmethod
    def to_row(dto: DeviceTemplateDTO) -> DbDeviceTemplate:
        return DbDeviceTemplate(
            name=dto.name,
            device_type=DbDeviceType[dto.device_type],
            width=dto.width,
            height=dto.height,
            user_agent=dto.user_agent,
        )

    @staticmethod
    def to_entity(row: DbDeviceTemplate) -> DeviceTemplate:
        entity = DeviceTemplate.from_attributes_without_validation(row)
        entity.device_type = DeviceType.Mobile if row.device_type == 2 else DeviceType.Desktop
        return entity
