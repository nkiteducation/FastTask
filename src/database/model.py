import enum

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from database.mixin import TimestampMixin, UUIDMixin

metadata = MetaData(
    naming_convention={
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
    }
)


class CoreModel(DeclarativeBase, AsyncAttrs):
    metadata = metadata

    @declared_attr
    def __tablename__(cls) -> str:
        return "".join(
            ["_" + c.lower() if c.isupper() else c for c in cls.__name__]
        ).lstrip("_")


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
class Board(CoreModel, UUIDMixin, TimestampMixin):
    title: Mapped[str]

    memberships: Mapped[list["UserUsingBoard"]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    members: Mapped[list["User"]] = relationship(
        secondary="user_using_board",
        viewonly=True,
        back_populates="member_boards",
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="board",
        order_by="Task.deadline",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Task(CoreModel, UUIDMixin, TimestampMixin):
    title: Mapped[str]
    description: Mapped[Optional[str]]

    deadline: Mapped[Optional[datetime]] = mapped_column(index=True)
    priority: Mapped[Priority] = mapped_column(
        SAEnum(Priority, name="priority_enum"), default=Priority.MEDIUM
    )
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, name="status_enum"), default=Status.TODO, index=True
    )

    board_id: Mapped[UUID] = mapped_column(
        ForeignKey("board.id", ondelete="CASCADE"), index=True
    )
    board: Mapped["Board"] = relationship(
        back_populates="tasks",
        passive_deletes=True,
    )

    assigned_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_user: Mapped[Optional["User"]] = relationship(
        back_populates="assigned_tasks",
        passive_deletes=True,
    )


class UserUsingBoard(CoreModel):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    board_id: Mapped[UUID] = mapped_column(
        ForeignKey("board.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="role_enum"), default=Role.USER
    )

    user: Mapped["User"] = relationship(
        back_populates="memberships",
        passive_deletes=True,
    )
    board: Mapped["Board"] = relationship(
        back_populates="memberships",
        passive_deletes=True,
    )


class User(CoreModel, UUIDMixin, TimestampMixin):
    name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]

    memberships: Mapped[list["UserUsingBoard"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    member_boards: Mapped[list["Board"]] = relationship(
        secondary="user_using_board",
        viewonly=True,
        back_populates="members",
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assigned_user",
        foreign_keys="[Task.assigned_user_id]",
        order_by="Task.deadline.desc()",
        passive_deletes=True,
    )
