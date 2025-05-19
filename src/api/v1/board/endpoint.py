from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    return {"board_id": board.id}


@router.delete(
    "/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_board(
    board_id: UUID,
    user: User = Depends(get_verification_user),
    session: AsyncSession = Depends(session_manager.session_scope),
):
    board = await session.get(Board, board_id)
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {board_id} not found",
        )

    result = await session.execute(
        select(UserUsingBoard).where(
            UserUsingBoard.board_id == board_id,
            UserUsingBoard.user_id == user.id,
        )
    )
    link = result.scalar_one_or_none()
    if link is None or link.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete this board",
        )

    await session.delete(board)
    await session.commit()


def serialize_participant(link: UserUsingBoard) -> dict:
    return {
        "id": str(link.user.id),
        "role": link.role,
    }


def serialize_task(task) -> dict:
    return {
        "id": str(task.id),
    }


def serialize_board(board) -> dict:
    return {
        "id": str(board.id),
        "title": board.title,
        "created_at": board.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": board.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "participants": [serialize_participant(link) for link in board.memberships],
        "tasks": [serialize_task(task) for task in board.tasks],
    }


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_all_boards(
    user: User = Depends(get_verification_user),
    session: AsyncSession = Depends(session_manager.session_scope),
):
    result = await session.execute(
        select(Board)
        .options(
            selectinload(Board.memberships).selectinload(UserUsingBoard.user),
            selectinload(Board.tasks),
        )
        .join(UserUsingBoard, UserUsingBoard.board_id == Board.id)
        .where(UserUsingBoard.user_id == user.id)
    )
    boards = result.scalars().unique().all()
    return {board.title: serialize_board(board) for board in boards}


@router.get(
    "/{board_id}",
    status_code=status.HTTP_200_OK,
)
async def get_boards(
    board_id: UUID,
    user: User = Depends(get_verification_user),
    session: AsyncSession = Depends(session_manager.session_scope),
):
    result = await session.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {board_id} not found",
        )
    return serialize_board(board)
