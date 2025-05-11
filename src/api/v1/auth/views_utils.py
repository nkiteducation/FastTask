from fastapi import HTTPException, status
from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import password_hash
from database.model import User


async def create_user_in_the_database(
    name: str, email: EmailStr, password: SecretStr, session: AsyncSession
):
    session.add(
        User(
            name=name,
            email=email,
            password_hash=password_hash(password.get_secret_value()),
        )
    )
    await session.commit()


async def generation_registration_error(user, session: AsyncSession):
    detail = []
    if await session.scalar(select(User).where(User.email == user.email)):
        detail.append("a user with this email address has already been registered")
    if await session.scalar(select(User).where(User.name == user.name)):
        detail.append("the username is already taken")
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=" and ".join(detail),
    )
