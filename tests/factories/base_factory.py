from typing import (
    TypeVar,
)

from polyfactory.factories.sqlalchemy_factory import (
    SQLAlchemyFactory,
    T,
)
from sqlalchemy import Column

from divine.shared.persistence.db_base import Base


M = TypeVar("M", bound=Base)


class BaseDbFactory(SQLAlchemyFactory[T]):
    """
    Based on
    https://polyfactory.litestar.dev/latest/usage/library_factories/sqlalchemy_factory.html#adding-global-overrides

    This base factory will set defaults when possible, except for default=None, because it cannot detect an actual default was set (yet)

    IT overloads `should_column_be_set` to skip automatic field generators, when there is a default or server default
    """

    # TODO: find a way to force defaults, __use_defaults__ won't work for SQLA factories
    # __async_persistence__ = SQLAASyncPersistence

    __is_base_factory__ = True
    __check_model__ = True
    __set_as_default_factory_for_type__ = True
    __set_server_defaults__ = True
    __use_defaults__ = True

    @classmethod
    def should_column_be_set(cls, column: Column) -> bool:
        """Variation of original method to skip columns with default and server default"""

        if not isinstance(column, Column):
            return False
        if not cls.__set_primary_key__ and column.primary_key:
            return False
        # Skip if column has SQLAlchemy default or server default

        # custom
        if not column.foreign_keys and cls.__use_defaults__ and bool(column.default):
            return False
        if not column.foreign_keys and cls.__set_server_defaults__:
            return not column.server_default

        # original
        return bool(cls.__set_foreign_keys__ or not column.foreign_keys)
