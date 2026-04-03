from fastapi import status
import pytest

from divine.devices.interface.views import (
    DeviceEndpoints,
)

from tests.factories.device_factory import TemplateMobileSchemaFactory


async def test_list_templates(integration_client):
    response = await integration_client.get(DeviceEndpoints.templates)

    assert response.status_code == status.HTTP_200_OK, response.json()
    payload = response.json()
    assert len(payload) == 21  # bulk added in migration


async def test_create_template(integration_client, test_name):
    body = TemplateMobileSchemaFactory.build(name=test_name, user_agent=test_name)
    response = await integration_client.post(DeviceEndpoints.templates, json=body.model_dump())

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    payload = response.json()
    assert payload["user_agent"] == test_name


async def test_create_from_non_existing_template(integration_client):
    body = {"template_id": 6666, "country_code": 620, "headers": {}}
    response = await integration_client.post(DeviceEndpoints.from_template, json=body)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {"detail": "Device Template 6666 not found"}


@pytest.mark.current
async def test_create_from_template(integration_client):
    body = {"template_id": 1, "country_code": 620, "headers": {}}
    response = await integration_client.post(DeviceEndpoints.from_template, json=body)

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    payload = response.json()
    assert payload["device_type"] == "Mobile"
    assert payload["country_code"] == 620


async def test_create_duplicate_template(integration_client, test_name):
    body = TemplateMobileSchemaFactory.build(name=test_name)
    await integration_client.post(DeviceEndpoints.templates, json=body.model_dump())
    response = await integration_client.post(DeviceEndpoints.templates, json=body.model_dump())

    assert response.status_code == status.HTTP_409_CONFLICT


async def test_create_from_template_invalid_country_code(integration_client):
    body = {"template_id": 1, "country_code": 9999, "headers": {}}
    response = await integration_client.post(DeviceEndpoints.from_template, json=body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
