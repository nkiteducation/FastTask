import re

from sqlalchemy import Enum
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from database.enum import UserRole

from .mixin import TimestampMixin, UUIDMixin


class CoreModel(DeclarativeBase, AsyncAttrs):
    @declared_attr
    def __tablename__(cls) -> str:
        s1 = re.sub(r"([^_])([A-Z])", r"\1-\2", cls.__name__)
        return s1.lower()


class User(CoreModel, UUIDMixin, TimestampMixin):
    user_name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(unique=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="role_enum", native_enum=True), default=UserRole.USER
    )
