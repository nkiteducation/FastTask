import datetime
import uuid

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False
    )
