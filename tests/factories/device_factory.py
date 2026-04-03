from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
import pycountry

from divine.devices.domain.entities import DeviceType
from divine.devices.interface.schemas import (
    DeviceCreateSchema,
    TemplateCreateSchema,
)
from divine.devices.persistence.db_models import (
    DbDeviceProfile,
    DbDeviceType,
)

from .base_factory import BaseDbFactory


POSIBLE_COUNTRY_CODES = [int(c.numeric) for c in pycountry.countries]


class DeviceFactory(BaseDbFactory[DbDeviceProfile]):
    # TODO(h): use the size provider for width and height
    device_type = Use(BaseDbFactory.__random__.choice, list(DbDeviceType))
    user_agent = BaseDbFactory.__faker__.user_agent
    country_code = Use(BaseDbFactory.__random__.choice, POSIBLE_COUNTRY_CODES)
    template_id = None
    deleted_at = None


class DesktopDeviceSchemaFactory(ModelFactory[DeviceCreateSchema]):
    device_type = DeviceType.Desktop
    size = BaseDbFactory.__faker__.mobile_window
    # TODO(h): user agent is random, should be fixed to desktop
    user_agent = BaseDbFactory.__faker__.user_agent
    country_code = Use(BaseDbFactory.__random__.choice, POSIBLE_COUNTRY_CODES)


class MobileDeviceSchemaFactory(ModelFactory[DeviceCreateSchema]):
    device_type = DeviceType.Mobile
    size = BaseDbFactory.__faker__.mobile_window
    # Use(BaseDbFactory.__random__.choice, list(DbDeviceType))
    # TODO(h): user agent is rangom, should be fixed to mobile
    user_agent = BaseDbFactory.__faker__.user_agent
    country_code = Use(BaseDbFactory.__random__.choice, POSIBLE_COUNTRY_CODES)


class TemplateMobileSchemaFactory(ModelFactory[TemplateCreateSchema]):
    name = ModelFactory.__faker__.unique.mobile_model
    device_type = DeviceType.Mobile
    size = BaseDbFactory.__faker__.mobile_window
    # TODO(h): user agent is random, should be fixed to mobile, it could be achieved with faker maybe
    user_agent = BaseDbFactory.__faker__.user_agent
