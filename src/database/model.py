import re

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

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
    admin: Mapped[bool] = mapped_column(default=False)
