from fastapi import status

from divine.devices.interface.views import DEVICE_RESOURCE


def test_retrieve_non_existing_device(mocker, test_client, mock_device_repo):
    mocker.patch.object(mock_device_repo, "find_by_id", return_value=None)
    response = test_client.get(f"{DEVICE_RESOURCE}/1234")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


def test_delete_non_existing_device(mocker, test_client, mock_device_repo):
    mocker.patch.object(mock_device_repo, "delete", return_value=False)
    response = test_client.delete(f"{DEVICE_RESOURCE}/4567")

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


def test_create_invalid_device(mocker, test_client, mock_device_repo):
    response = test_client.post(DEVICE_RESOURCE, json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.json()
