from fastapi import status

from divine.extensions.pydantic_extensions import model_dump_no_secrets
from divine.users.interface.views import USER_RESOURCE

from tests.factories.user_factory import (
    UserFactory,
    UserSchemaFactory,
)


async def test_create_user(integration_client, test_name):
    schema = UserSchemaFactory.build(first_name=test_name)
    request_payload = model_dump_no_secrets(schema, reveal_secrets={"password"})
    response = await integration_client.post(USER_RESOURCE, json=request_payload)

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    payload = response.json()
    assert payload["first_name"] == test_name


async def test_create_user_exists(integration_client, test_name):
    email_exists = "exist@test.com"
    _ = await UserFactory.create_async(email=email_exists)

    schema = UserSchemaFactory.build(email=email_exists)
    request_payload = model_dump_no_secrets(schema, reveal_secrets={"password"})
    response = await integration_client.post(USER_RESOURCE, json=request_payload)

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
