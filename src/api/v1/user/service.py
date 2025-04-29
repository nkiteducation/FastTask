from typing import Any, Sequence
from uuid import UUID

from pydantic import EmailStr, SecretStr
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import get_password_hash
from database.model import User


async def get_all_users(
    session: AsyncSession, *, limit: int = 100, offset: int = 0
) -> Sequence[User]:
    result = await session.execute(
        select(User).order_by(User.id).limit(limit).offset(offset)
    )
    return result.scalars().all()


async def get_user(user_id: UUID, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one()

async def update_user(
    user_id: UUID,
    session: AsyncSession,
    update_data: dict[str, Any],
) -> User:
    pwd: SecretStr | None = update_data.pop("password", None)
    if pwd is not None:
        update_data["password_hash"] = get_password_hash(pwd.get_secret_value())

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
        .returning(User)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def delete_user(user_id: UUID, session: AsyncSession) -> User:
    result = await session.execute(
        delete(User).where(User.id == user_id).returning(User)
    )
    return result.scalar_one()

