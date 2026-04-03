from datetime import datetime
from typing import ClassVar

from passlib.context import CryptContext
from sqlalchemy import (
    DateTime,
    func,
    String,
    TypeDecorator,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class TimedMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # database default
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        onupdate=func.now(),
    )


class ReprMixin:
    id: ClassVar

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.id}>"


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordType(TypeDecorator):
    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Hash on save."""
        if value is None:
            return None
        if not pwd_context.identify(value):  # not already hashed
            return pwd_context.hash(value)
        return value

    def process_result_value(self, value, dialect):
        """Return as-is on load."""
        return value
