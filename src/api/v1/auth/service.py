from datetime import timedelta
from typing import Callable

from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import encode_jwt, password_hash
from core.settings import config
from database.model import User

TOKEN_TYPE_FIELD = "type"
ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"


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


async def is_email_taken(email: str, session: AsyncSession) -> bool:
    return await session.scalar(select(User).where(User.email == email)) is not None


async def is_name_taken(name: str, session: AsyncSession) -> bool:
    return await session.scalar(select(User).where(User.name == name)) is not None


def jwt_factory(
    token_type: str,
    lifetime: timedelta,
) -> Callable[[dict[str, any]], str]:
    def create_token(payload: dict[str, any]) -> str:
        data = payload.copy()
        data[TOKEN_TYPE_FIELD] = token_type
        return encode_jwt(data, lifetime)

    return create_token


def build_jwt_payload(user: User) -> dict:
    return {
        "sub": str(user.id),
        "username": user.name,
        "email": user.email,
    }


get_access_token = jwt_factory(ACCESS_TYPE, config.jwt.access_token_lifetime)
get_refresh_token = jwt_factory(REFRESH_TYPE, config.jwt.refresh_token_lifetime)
