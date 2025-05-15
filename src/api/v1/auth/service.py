from datetime import timedelta
from typing import Callable

from fastapi import HTTPException, status
from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import encode_jwt, password_hash
from core.settings import config
from database.model import User

TOKEN_TYPE_FIELD = "type"


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


def jwt_factory(
    token_type: str,
    lifetime: timedelta,
) -> Callable[[dict[str, any]], str]:
    def create_token(payload: dict[str, any]) -> str:
        data = payload.copy()
        data[TOKEN_TYPE_FIELD] = token_type
        return encode_jwt(data, lifetime)

    return create_token


get_access_token = jwt_factory("access", config.jwt.access_token_lifetime)
get_refresh_token = jwt_factory("refresh", config.jwt.refresh_token_lifetime)
