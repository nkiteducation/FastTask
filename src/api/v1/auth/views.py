from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.v1.auth.utils import decode_jwt, encode_jwt, verify_password, password_hash
from api.v1.shemas import UserDTO, UserCreate
from database.model import User
from database.session import session_manager

http_barare = HTTPBearer()


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


router = APIRouter(prefix="/jwt", tags=["JWT"])


@router.post("/login/", response_model=TokenInfo)
def login_user():
    pass


async def register_user_in_db(
    name: str, email: EmailStr, password: SecretStr, session: AsyncSession
) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=password_hash(password.get_secret_value()),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/register/", response_model=TokenInfo)
async def register_user(
    user: UserCreate, session: AsyncSession = Depends(session_manager.session_scope)
):
    try:
        db_user = await register_user_in_db(**user.model_dump(), session=session)
    except IntegrityError:
        detail = []
        await session.rollback()
        if await session.scalar(sql.select(User).where(User.email == user.email)):
            detail.append("a user with this email address has already been registered")
        if await session.scalar(sql.select(User).where(User.name == user.name)):
            detail.append("the username is already taken")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=" and ".join(detail) or "Registration error",
        )

    token = encode_jwt(
        {
            "sub": str(db_user.id),
            "name": db_user.name,
            "email": db_user.email,
        }
    )
    return TokenInfo(access_token=token, token_type="Bearer")
