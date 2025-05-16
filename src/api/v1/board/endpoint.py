from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.dependencies import get_verification_user
from database.model import Board, Role, User, UserUsingBoard
from database.session import session_manager

router = APIRouter(prefix="/board", tags=["Board"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_board(
    title: str,
    user: User = Depends(get_verification_user),
    session: AsyncSession = Depends(session_manager.session_scope),
):
    board = Board(title=title)
    session.add(board)
    await session.flush()

    link = UserUsingBoard(board_id=board.id, user_id=user.id, role=Role.ADMIN)
    session.add(link)
    await session.commit()

    return {"board_id": board.id, "message": "Board created and user added as admin"}
