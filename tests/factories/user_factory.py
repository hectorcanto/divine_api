from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from divine.users.interface.schemas import UserCreateSchema
from divine.users.persistence.db_models import DbUser

from .base_factory import BaseDbFactory


class UserFactory(BaseDbFactory[DbUser]):
    email = Use(BaseDbFactory.__faker__.unique.email, domain="divine.com")


class UserSchemaFactory(ModelFactory[UserCreateSchema]):
    email = BaseDbFactory.__faker__.unique.email
    first_name = BaseDbFactory.__faker__.first_name
    last_name = BaseDbFactory.__faker__.last_name
