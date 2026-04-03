from abc import (
    ABC,
    abstractmethod,
)

from divine.users.domain.entities import UserId

from .entities import (
    DeviceFromTemplateDTO,
    DeviceId,
    DeviceProfile,
    DeviceProfileDTO,
    DeviceProfileNullableDTO,
    DeviceTemplate,
    DeviceTemplateDTO,
)


class BaseDeviceRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UserId, device_id: DeviceId) -> DeviceProfile | None: ...

    @abstractmethod
    async def list(self, user_id: UserId) -> list[DeviceProfile]: ...

    @abstractmethod
    async def insert(self, user_id: UserId, device_profile: DeviceProfileDTO) -> DeviceProfile: ...

    @abstractmethod
    async def insert_from_template(self, user_id: UserId, dto: DeviceFromTemplateDTO) -> DeviceProfile: ...

    @abstractmethod
    async def update(self, user_id: UserId, device_profile: DeviceProfileNullableDTO) -> DeviceProfile: ...

    @abstractmethod
    async def delete(self, user_id: UserId, device_id: DeviceId) -> bool: ...

    @abstractmethod
    async def list_templates(self) -> list[DeviceTemplate]: ...

    @abstractmethod
    async def insert_template(self, dto: DeviceTemplateDTO) -> DeviceTemplate: ...
