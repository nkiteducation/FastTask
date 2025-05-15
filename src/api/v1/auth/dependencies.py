from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import decode_jwt, verify_password
from api.v1.users.shemas import UserCreate, UserDTO
from database.model import User
from database.session import session_manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def get_form_user(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[SecretStr, Form()],
):
    return UserCreate(name=username, email=email, password=password)


async def validate_auth_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(session_manager.session_scope),
) -> UserDTO:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    user = await session.scalar(select(User).where(User.name == username))
    if not user or not verify_password(password, user.password_hash):
        raise unauthed_exc

    return UserDTO.model_validate(user)


def verification_refresh_jwt(
    token: Annotated[
        str | None, Cookie(alias="refresh-token", include_in_schema=False)
    ] = None,
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cookie ‘refresh_token’ not found",
        )
    try:
        return decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verification_access_jwt(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        return decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_verification_user(
    payload: dict = Depends(verification_access_jwt),
    session: AsyncSession = Depends(session_manager.session_scope),
):
    user_in_db = await session.get(User, UUID(payload.get("sub")))
    return UserDTO.model_validate(user_in_db)
