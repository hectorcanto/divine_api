from divine.devices.domain.entities import DeviceType
from divine.devices.persistence.db_models import DbDeviceType


def test_device_type_to_db():
    assert DbDeviceType["Desktop"] == DbDeviceType.Desktop
    assert DbDeviceType[DeviceType.Desktop] == DbDeviceType.Desktop
