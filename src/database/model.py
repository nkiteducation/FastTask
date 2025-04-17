import datetime
import enum
import re
import uuid

import sqlalchemy as sa

from sqlalchemy import Enum
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
class User(CoreModel, UUIDMixin, TimestampMixin):
    name: Mapped[str] = mapped_column(sa.String(50))
    email: Mapped[str] = mapped_column(sa.String(100), unique=True)
    password: Mapped[str] = mapped_column(sa.String(100))
    
    rooms: Mapped[list["RoomMembership"]] = relationship("RoomMembership", back_populates="user")
    assignments: Mapped[list["Task"]] = relationship("Task", back_populates="assigned_to")
    
class Task(UUIDMixin, TimestampMixin, CoreModel):
    title: Mapped[str] = mapped_column(sa.String, )
    description: Mapped[str | None] = mapped_column(sa.Text)
    deadline: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.TODO)
    
    room_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("room.id"))
    created_by_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("user.id"))
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("user.id"))
    
    created_by: Mapped["User"] = relationship("User")
    assigned_to: Mapped["User"] = relationship("User", back_populates="assignments")
    room: Mapped["Room"] = relationship("Room", back_populates="tasks")
    
class Room(UUIDMixin, TimestampMixin, CoreModel):
    name: Mapped[str] = mapped_column(sa.String(50))
    description: Mapped[str | None] = mapped_column(sa.Text)
    
    created_by_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("user.id"))
    
    created_by: Mapped["User"] = relationship("User")
    members: Mapped[list["RoomMembership"]] = relationship("RoomMembership", back_populates="room")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="room")
    
class RoomMembership(TimestampMixin, CoreModel):
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("user.id"), primary_key=True)
    room_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("room.id"), primary_key=True)
    
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.USER)

    user: Mapped["User"] = relationship("User", back_populates="rooms")
    room: Mapped["Room"] = relationship("Room", back_populates="members")