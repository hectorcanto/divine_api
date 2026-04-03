import pytest

from divine.devices.domain.entities import DeviceType
from divine.devices.persistence.postgres_repository import PostgresDeviceProfileRepository
from divine.users.persistence.postgres_repository import PostgresUserRepository

from tests.factories.device_factory import DeviceFactory
from tests.factories.user_factory import UserFactory


@pytest.mark.current
@pytest.mark.users
async def test_user_factory(test_db_session, test_name):
    user = await UserFactory.create_async(first_name=test_name, last_name=test_name)
    assert user.id
    _ = await UserFactory.create_async()
    repo = PostgresUserRepository(test_db_session)
    factory_users = await repo.list()

    assert len(factory_users) == 5  # = 2 here + 1 migration + 2  from session fixtures (auth_user and another_user)
    assert factory_users[2].first_name == "Super"
    assert factory_users[2].last_name == "Cow"
    assert factory_users[3].first_name == test_name
    assert factory_users[3].last_name == test_name


@pytest.mark.devices
async def test_device_factory(test_db_session, auth_user):
    _ = await DeviceFactory.create_async(user_id=auth_user)
    repo = PostgresDeviceProfileRepository(test_db_session)
    items = await repo.list(user_id=auth_user)

    assert len(items) == 1
    assert isinstance(items[0].device_type, DeviceType)
