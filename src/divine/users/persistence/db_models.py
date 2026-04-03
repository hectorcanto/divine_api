"""All DB models, convert into package if needed

Maintenance:
- favor prefix `Db` to differentiate db models with other kinds of object
"""

from datetime import (
    datetime,
)

from sqlalchemy import (
    DateTime,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from divine.extensions.db_extensions import (
    PasswordType,
    pwd_context,
    ReprMixin,
    TimedMixin,
)
from divine.shared.persistence.db_base import Base
from divine.users.domain.entities import UserId


class DbUser(Base, TimedMixin, ReprMixin):
    """Basic user definition,  usable for multiple purposes"""

    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(primary_key=True, autoincrement=True)
    # I prefer integer for simplicity, an UUID could be used as public id

    # NOTE personal data is plain, it needs to be better protected
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)

    password: Mapped[str] = mapped_column(PasswordType, nullable=False)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    # devices = relationship("DbDeviceProfile", back_populates="users")
