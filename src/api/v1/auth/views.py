from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import select
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
    session: AsyncSession = Depends(session_manager.session_scope),
) -> UserDTO:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await session.scalar(select(User).where(User.name == username))
    if not user or not verify_password(password, user.password_hash):
        raise unauthed_exc

    return UserDTO.model_validate(user)


@router.post("/token", response_model=TokenInfo)
def login_user(user: UserDTO = Depends(validate_auth_user)):
    token = encode_jwt(
        {
            "sub": str(user.id),
        },
        timedelta(minutes=15),
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
    await session.refresh(user)
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(
    user: UserCreate, session: AsyncSession = Depends(session_manager.session_scope)
):
    try:
        return await register_user_in_db(**user.model_dump(), session=session)
    except IntegrityError:
        await session.rollback()
        detail = []
        if await session.scalar(select(User).where(User.email == user.email)):
            detail.append("a user with this email address has already been registered")
        if await session.scalar(select(User).where(User.name == user.name)):
            detail.append("the username is already taken")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=" and ".join(detail),
        )


def get_payload_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_auth_user(
    payload: dict = Depends(get_payload_jwt),
    session: AsyncSession = Depends(session_manager.session_scope),
) -> User:
    return await session.get(User, UUID(payload.get("sub")))


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_auth_user)):
    return UserRead.model_validate(user)
