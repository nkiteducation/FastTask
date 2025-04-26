from uuid import uuid4

import faker
import pytest

from database.model import Board, Priority, Role, Status, Task, User, UserUsingBoard
from database.session import SessionManager


@pytest.mark.asyncio
async def test_user(fake: faker.Faker, session_manager: SessionManager):
    fake_user = {
        "name": fake.name(),
        "email": fake.email(),
        "password_hash": fake.password(),
    }
    async with session_manager.session_scope() as session:
        user = User(**fake_user)
        session.add(user)
        await session.commit()
        await session.refresh(user)


@pytest.mark.asyncio
async def test_board(fake: faker.Faker, session_manager: SessionManager):
    title = fake.name()
    async with session_manager.session_scope() as session:
        board = Board(title=title)
        session.add(board)
        await session.commit()
        await session.refresh(board)


@pytest.mark.asyncio
async def test_task(fake: faker.Faker, session_manager: SessionManager):
    fake_tasc = {
        "title": fake.name(),
        "description": fake.text(),
        "deadline": fake.date_time(),
        "priority": fake.enum(Priority),
        "status": fake.enum(Status),
    }
    async with session_manager.session_scope() as session:
        task = Task(**fake_tasc, board_id=uuid4())
        session.add(task)
        await session.commit()
        await session.refresh(task)


@pytest.mark.asyncio
async def test_user_using_board(fake: faker.Faker, session_manager: SessionManager):
    fake_user = {
        "name": fake.name(),
        "email": fake.email(),
        "password_hash": fake.password(),
    }
    fake_board = {"title": fake.name()}
    async with session_manager.session_scope() as session:
        user = User(**fake_user)
        board = Board(**fake_board)
        session.add_all([user, board])

        await session.flush()

        link = UserUsingBoard(
            user_id=user.id,
            board_id=board.id,
            role=Role.ADMIN,
        )
        session.add(link)
