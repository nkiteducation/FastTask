from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
)
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import sql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import decode_jwt, encode_jwt, password_hash, verify_password
from api.v1.shemas import UserCreate, UserDTO, UserRead
from database.model import User
from database.session import session_manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


router = APIRouter(prefix="/auth", tags=["JWT"])


async def validate_auth_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session=Depends(session_manager.session_scope),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if not (
        user := await session.scalar(sql.select(User).where(User.name == username))
    ):
        raise unauthed_exc

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise unauthed_exc

    return UserDTO.model_validate(user)


@router.post("/token", response_model=TokenInfo)
def login_user(user: UserDTO = Depends(validate_auth_user)):
    token = encode_jwt(
        {
            "sub": str(user.id),
            "username": user.name,
            "email": user.email,
        }
    )
    return TokenInfo(access_token=token, token_type="Bearer")


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


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate, session: AsyncSession = Depends(session_manager.session_scope)
):
    try:
        await register_user_in_db(**user.model_dump(), session=session)
    except IntegrityError:
        detail = []
        await session.rollback()
        if await session.scalar(sql.select(User).where(User.email == user.email)):
            detail.append("a user with this email address has already been registered")
        if await session.scalar(sql.select(User).where(User.email == user.email)):
            detail.append("the username is already taken")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=" and ".join(detail) or "Registration error",
        )


def get_payload_jwt(token: str = Depends(oauth2_scheme)):
    return decode_jwt(token)


async def get_auth_user(
    payload_jwt: dict = Depends(get_payload_jwt),
    session: AsyncSession = Depends(session_manager.session_scope),
) -> UserDTO:
    user_in_db = await session.get(User, UUID(payload_jwt.get("sub")))
    return UserDTO.model_validate(user_in_db)


@router.post("/me", response_model=UserRead)
async def me(user: UserDTO = Depends(get_auth_user)):
    return UserRead.model_validate(user)
