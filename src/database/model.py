import enum
import re

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Table, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from .mixin import TimestampMixin, UUIDMixin


# -------------------- CORE MODEL --------------------
class CoreModel(DeclarativeBase, AsyncAttrs):
    @declared_attr
    def __tablename__(cls) -> str:
        s1 = re.sub(r"([^_])([A-Z])", r"\1-\2", cls.__name__)
        return s1.lower()


# -------------------- ENUMS --------------------
class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# -------------------- MODELS --------------------
user_tasks = Table(
    "user-tasks",
    CoreModel.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("task_id", ForeignKey("task.id"), primary_key=True),
)


class User(CoreModel, TimestampMixin, UUIDMixin):
    name: Mapped[str]
    email: Mapped[str]
    password_hesh: Mapped[str]
    role: Mapped[Role]

    tasks: Mapped[list["Task"]] = relationship(
        secondary=user_tasks,
        back_populates="user_tasks",
    )


class Task(CoreModel, TimestampMixin, UUIDMixin):
    title: Mapped[str]
    description: Mapped[str | None]
    deadline: Mapped[datetime | None]
    priority: Mapped[Priority] = mapped_column(default=Priority.MEDIUM)
    status: Mapped[Status] = mapped_column(default=Status.TODO)

    user_tasks: Mapped["User"] = relationship(
        secondary=user_tasks,
        back_populates="tasks",
    )
