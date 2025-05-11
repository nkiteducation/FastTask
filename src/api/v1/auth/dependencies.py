from typing import Annotated

from fastapi import Depends, Form, HTTPException, status
from pydantic import EmailStr, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.utils import verify_password
from api.v1.shemas import UserCreate, UserDTO
from database.model import User
from database.session import session_manager


def get_form_user(
    name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[SecretStr, Form()],
):
    return UserCreate(name=name, email=email, password=password)


async def validate_auth_user(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(session_manager.session_scope),
) -> UserDTO:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    user = await session.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise unauthed_exc

    return UserDTO.model_validate(user)
