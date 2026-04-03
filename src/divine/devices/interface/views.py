from dataclasses import dataclass
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)

from divine.dependencies import inject_device_repo
from divine.devices.persistence.postgres_repository import PostgresDeviceProfileRepository
from divine.shared.auth import get_current_user
from divine.users.persistence.db_models import DbUser

from ..domain.entities import (
    DeviceId,
    DeviceProfile,
    DeviceProfileNullableDTO,
    DeviceTemplate,
)
from ..domain.exceptions import (
    DeviceProfileNotFoundError,
    DeviceTemplateNotFoundError,
    TemplateNameAlreadyExistsError,
)
from ..domain.repository_interface import BaseDeviceRepository
from .schemas import (
    DeviceCreateFromTemplateSchema,
    DeviceCreateSchema,
    DevicePatchSchema,
    TemplateCreateSchema,
)


logger = logging.getLogger(__name__)
DEVICE_RESOURCE = "/device-profiles"
TEMPLATES_SUBRESOURCE = "/templates"
devices_router = APIRouter(
    prefix=DEVICE_RESOURCE,
    tags=["devices"],
)


@dataclass(frozen=True, slots=True)
class DeviceEndpoints:
    templates = DEVICE_RESOURCE + TEMPLATES_SUBRESOURCE
    from_template = DEVICE_RESOURCE + "/from_template"


@devices_router.post("/", response_model=DeviceProfile, status_code=status.HTTP_201_CREATED)
async def create_device_profile(
    body: DeviceCreateSchema,
    user: DbUser = Depends(get_current_user),
    repository: BaseDeviceRepository | PostgresDeviceProfileRepository = Depends(inject_device_repo),
):
    new_device = await repository.insert(user.id, body.to_dto())
    logger.info(f"Created new device_id={new_device.id}")
    return new_device


@devices_router.get("/templates", response_model=list[DeviceTemplate])
async def list_device_templates(
    repository: BaseDeviceRepository | PostgresDeviceProfileRepository = Depends(inject_device_repo),
):
    return await repository.list_templates()


@devices_router.get("/{device_id}", response_model=DeviceProfile)
async def retrieve_device_profile(
    device_id: Annotated[DeviceId, Path(gt=0)],
    user: DbUser = Depends(get_current_user),
    repository: BaseDeviceRepository = Depends(inject_device_repo),
):
    device = await repository.find_by_id(user.id, device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DeviceProfile {device_id} not found",
        )
    return device


@devices_router.get("/", response_model=list[DeviceProfile])
async def list_device_profiles(
    user: DbUser = Depends(get_current_user),
    repository: PostgresDeviceProfileRepository | BaseDeviceRepository = Depends(inject_device_repo),
):
    return await repository.list(user.id)


@devices_router.patch("/{device_id}", response_model=DeviceProfile)
async def patch_device_profile(
    device_id: DeviceId,
    body: DevicePatchSchema,
    user: DbUser = Depends(get_current_user),
    repository: PostgresDeviceProfileRepository | BaseDeviceRepository = Depends(inject_device_repo),
):
    patch = DeviceProfileNullableDTO(
        id=device_id,
        **body.model_dump(exclude_none=True, exclude_unset=True),
    )
    try:
        patched = await repository.update(user.id, patch)
    except DeviceProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DeviceProfile {device_id} not found",
        )
    logger.info(f"Patched device_id={device_id}")
    return patched


@devices_router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_profile(
    device_id: DeviceId,
    user: DbUser = Depends(get_current_user),
    repository: PostgresDeviceProfileRepository | BaseDeviceRepository = Depends(inject_device_repo),
):
    deleted = await repository.delete(user.id, device_id)
    if not deleted:
        logger.warning(f"Device profile with device_id={device_id} does not exist or it was already deleted")
    else:
        logger.info(f"Deleted device_id={device_id}")


@devices_router.post(TEMPLATES_SUBRESOURCE, status_code=status.HTTP_201_CREATED)
async def create_template(
    body: TemplateCreateSchema,
    repository: PostgresDeviceProfileRepository | BaseDeviceRepository = Depends(inject_device_repo),
):
    try:
        template = await repository.insert_template(body.to_dto())
    except TemplateNameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A Device Template with name {body.name} already exists",
        )
    logger.info(f"Created template with template_id={template.id} and name={template.name}")
    return template


@devices_router.post("/from_template", status_code=status.HTTP_201_CREATED, response_model=DeviceProfile)
async def create_device_from_template(
    body: DeviceCreateFromTemplateSchema,
    user: DbUser = Depends(get_current_user),
    repository: PostgresDeviceProfileRepository | BaseDeviceRepository = Depends(inject_device_repo),
):
    try:
        device = await repository.insert_from_template(user.id, body.to_dto())
    except DeviceTemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device Template {body.template_id} not found",
        )
    return device
