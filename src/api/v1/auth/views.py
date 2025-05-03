from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import decode_jwt, encode_jwt, verify_password
from database.model import User
from database.session import session_manager

http_barare = HTTPBearer()


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class AuthUser(BaseModel):
    name: str
    email: EmailStr
    id: UUID


router = APIRouter(prefix="/jwt", tags=["JWT"])


async def validate_auth_user(
    email: Annotated[EmailStr, Form],
    password: Annotated[SecretStr, Form],
    session: AsyncSession = Depends(session_manager.session_scope),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )

    if not (
        user := (
            await session.execute(sql.select(User).where(User.email == email))
        ).scalar_one_or_none()
    ):
        raise unauthed_exc
    elif not verify_password(password.get_secret_value(), user.password_hash):
        raise unauthed_exc

    return AuthUser.model_validate(user, from_attributes=True)


def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_barare)],
):
    try:
        payload = decode_jwt(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid token"
        )
    print(payload)
    return payload


async def get_current_auth_user(
    payload: Annotated[dict, Depends(get_jwt_payload)],
    session: AsyncSession = Depends(session_manager.session_scope),
):
    uid = UUID(payload.get("sub"))
    user = await session.get(User, uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid"
        )

    return user


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: AuthUser = Depends(validate_auth_user),
):
    jwt_payload = {"sub": str(user.id), "name": user.name, "email": user.email}
    token = encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )


@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_jwt_payload),
    user: User = Depends(get_current_auth_user),
):
    return {
        "username": user.name,
        "email": user.email,
        "logged_in_at": payload.get("iat"),
    }
