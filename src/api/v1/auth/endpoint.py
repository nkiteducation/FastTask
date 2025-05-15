from datetime import timedelta
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.dependencies import (
    validate_auth_user,
    verification_access_jwt,
    verification_refresh_jwt,
)
from api.v1.auth.utils import encode_jwt, password_hash
from api.v1.users.shemas import UserCreate, UserDTO
from core.settings import config
from database.model import User
from database.session import session_manager

router = APIRouter(prefix="/auth", tags=["auth"])

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


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,  # = Depends(get_form_user) <- in case it turns out you need to do it from a form.  # noqa: E501
    session: AsyncSession = Depends(session_manager.session_scope),
):
    try:
        await create_user_in_the_database(**user.model_dump(), session=session)
    except IntegrityError:
        await session.rollback()
        raise await generation_registration_error(user, session)


@router.post("/token", response_model=TokenInfo)
def login_user(response: Response, user: UserDTO = Depends(validate_auth_user)):
    response.set_cookie(
        "refresh-token",
        get_refresh_token({"sub": str(user.id)}),
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=config.jwt.refresh_token_lifetime,
    )
    return TokenInfo(
        access_token=get_access_token(
            {"sub": str(user.id), "username": user.name, "email": user.email}
        )
    )


@router.post("/refresh", response_model=TokenInfo)
async def refresh_access_token(
    payload: dict = Depends(verification_refresh_jwt),
    session: AsyncSession = Depends(session_manager.session_scope),
):
    user = await session.get(User, UUID(payload.get("sub")))
    return TokenInfo(
        access_token=get_access_token(
            {"sub": str(user.id), "username": user.name, "email": user.email}
        )
    )


@router.get("/me")
async def me(me: dict = Depends(verification_access_jwt)):
    return "Ok"
