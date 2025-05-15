from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.dependencies import (
    validate_auth_user,
    verification_access_jwt,
    verification_refresh_jwt,
)
from api.v1.auth.service import (
    create_user_in_the_database,
    generation_registration_error,
    get_access_token,
    get_refresh_token,
)
from api.v1.users.shemas import UserCreate, UserDTO
from core.settings import config
from database.model import User
from database.session import session_manager

router = APIRouter(prefix="/auth", tags=["auth"])


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
