from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.views_utils import (
    create_user_in_the_database,
    generation_registration_error,
)
from api.v1.shemas import UserCreate
from database.session import session_manager

router = APIRouter(prefix="/auth", tags=["JWT"])


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
