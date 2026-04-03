from fastapi import status

from divine.devices.interface.views import DEVICE_RESOURCE
from divine.devices.persistence.postgres_repository import PostgresDeviceProfileRepository

from tests.factories.device_factory import (
    DeviceFactory,
    MobileDeviceSchemaFactory,
)


# pytestmark = [pytest.mark.current]


async def test_get_device(integration_client, auth_user):
    device = await DeviceFactory.create_async(user_id=auth_user)
    route = f"{DEVICE_RESOURCE}/{device.id}"
    response = await integration_client.get(route)

    assert response.status_code == status.HTTP_200_OK, response.json()
    payload = response.json()
    assert payload["id"] == device.id


async def test_get_device_from_auth_user_with_another_user(integration_client, another_user):
    device = await DeviceFactory.create_async(user_id=another_user)
    route = f"{DEVICE_RESOURCE}/{device.id}"
    response = await integration_client.get(route)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


async def test_list_devices(integration_client, auth_user, another_user):
    await DeviceFactory.create_batch_async(size=4, user_id=auth_user)
    await DeviceFactory.create_batch_async(size=2, user_id=another_user)
    # those 2 devices should not appear
    route = DEVICE_RESOURCE + "/"
    response = await integration_client.get(route)

    assert response.status_code == status.HTTP_200_OK, response.json()
    payload = response.json()
    assert len(payload) == 4


async def test_create_device(integration_client, test_name):
    schema = MobileDeviceSchemaFactory.build()
    route = DEVICE_RESOURCE + "/"
    response = await integration_client.post(route, json=schema.model_dump())
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    payload = response.json()
    assert payload["device_type"] == "Mobile"
    assert payload["user_agent"] == schema.user_agent


async def test_delete_device(integration_client, test_db_session, auth_user):
    device = await DeviceFactory.create_async(id=1234, user_id=auth_user)
    route = f"{DEVICE_RESOURCE}/{device.id}"

    repo = PostgresDeviceProfileRepository(test_db_session)
    saved_device = await repo.find_by_id(auth_user, device.id)
    assert saved_device

    response = await integration_client.delete(route)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
    removed_device = await repo.find_by_id(auth_user, device.id)
    assert removed_device is None


async def test_patch_device(integration_client, auth_user, test_name):
    device = await DeviceFactory.create_async(user_id=auth_user)
    route = f"{DEVICE_RESOURCE}/{device.id}"
    response = await integration_client.patch(route, json={"user_agent": test_name})

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["user_agent"] == test_name


async def test_patch_non_existing_device(integration_client, test_name):
    response = await integration_client.patch(f"{DEVICE_RESOURCE}/99999", json={"user_agent": test_name})

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_patch_device_invalid_country_code(integration_client, auth_user):
    device = await DeviceFactory.create_async(user_id=auth_user)
    route = f"{DEVICE_RESOURCE}/{device.id}"
    response = await integration_client.patch(route, json={"country_code": 9999})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_patch_device_empty_body(integration_client, auth_user):
    device = await DeviceFactory.create_async(user_id=auth_user)
    response = await integration_client.patch(f"{DEVICE_RESOURCE}/{device.id}", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_create_device_invalid_country_code(integration_client):
    schema = MobileDeviceSchemaFactory.build()
    payload = schema.model_dump()
    payload["country_code"] = 9999
    response = await integration_client.post(DEVICE_RESOURCE + "/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
