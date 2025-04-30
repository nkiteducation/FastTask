from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.shemas import UserInput, UserReturn, UserUpdate
from api.v1.user.service import (
    delete_user,
    get_all_users,
    get_user,
    update_user,
)
from database.session import session_manager

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/", response_model=list[UserReturn])
async def list_users(session=Depends(session_manager.session_scope)):
    users = await get_all_users(session)
    return [UserReturn.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserReturn)
async def retrieve_user(user_id: UUID, session=Depends(session_manager.session_scope)):
    user = await get_user(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserReturn.model_validate(user)


@router.put("/{user_id}", response_model=UserReturn)
async def full_update_user(
    user_id: UUID,
    data: UserInput,
    session=Depends(session_manager.session_scope),
):
    updated = await update_user(user_id, data.model_dump(), session)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserReturn.model_validate(updated)


@router.patch("/{user_id}", response_model=UserReturn)
async def partial_update_user_route(
    user_id: UUID,
    data: UserUpdate,
    session=Depends(session_manager.session_scope),
):
    updated = await update_user(user_id, data.model_dump(exclude_unset=True), session)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserReturn.model_validate(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    user_id: UUID, session=Depends(session_manager.session_scope)
):
    deleted = await delete_user(user_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
