import enum
import re

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
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
class User(CoreModel, TimestampMixin, UUIDMixin):
    name: Mapped[str]
    email: Mapped[str]
    password_hesh: Mapped[str]

    board_links: Mapped[list["UserUsingBoard"]] = relationship(back_populates="user")
    boards: Mapped[list["Board"]] = relationship(
        secondary="user-using-board", viewonly=True, back_populates="participants"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assigned_user",
        cascade="all, delete-orphan",
        foreign_keys="[Task.assigned_user_id]",
    )


class Board(CoreModel, TimestampMixin, UUIDMixin):
    title: Mapped[str]

    user_links: Mapped[list["UserUsingBoard"]] = relationship(back_populates="board")
    participants: Mapped[list["User"]] = relationship(
        secondary="user-using-board", viewonly=True, back_populates="boards"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="board", cascade="all, delete-orphan"
    )


class Task(CoreModel, TimestampMixin, UUIDMixin):
    title: Mapped[str]
    description: Mapped[str | None]
    deadline: Mapped[datetime | None]
    priority: Mapped[Priority] = mapped_column(default=Priority.MEDIUM)
    status: Mapped[Status] = mapped_column(default=Status.TODO)

    board_id: Mapped[UUID] = mapped_column(ForeignKey("board.id"))
    board: Mapped["Board"] = relationship(back_populates="task")
    assigned_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    assigned_user: Mapped["User"] = relationship(back_populates="assigned_tasks")


class UserUsingBoard(CoreModel):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    board_id: Mapped[UUID] = mapped_column(ForeignKey("board.id"), primary_key=True)
    role: Mapped[Role] = mapped_column(default=Role.USER)

    user: Mapped["User"] = relationship(back_populates="board_links")
    board: Mapped["Board"] = relationship(back_populates="user_links")
