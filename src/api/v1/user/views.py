from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from api.v1.shemas import UserInput, UserReturn
from api.v1.user.service import delete_user, get_all_users, get_user, update_user
from database.session import session_manager

router = APIRouter(prefix="/user")


@router.get("/", response_model=list[UserReturn])
async def all_user(session=Depends(session_manager.session_scope)):
    sequence_users = await get_all_users(session)
    return [
        UserReturn.model_validate(user, from_attributes=True) for user in sequence_users
    ]


@router.get("/{user_id}", response_model=UserReturn)
async def get_item(
    user_id: UUID, session=Depends(session_manager.session_scope)
):
    user = await get_user(user_id, session)
    return UserReturn.model_validate(user, from_attributes=True)


@router.put("/items/{user_id}", response_model=UserReturn)
async def update_item(
    user_id: UUID,
    updated: UserInput,
    session=Depends(session_manager.session_scope),
):
    up_user = await update_user(
        user_id=user_id,
        update_data=updated.model_dump(),
        session=session,
    )
    return UserReturn.model_validate(up_user, from_attributes=True)

@router.delete("/items/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    user_id: UUID,
    session=Depends(session_manager.session_scope),
):
    await delete_user(user_id, session)
