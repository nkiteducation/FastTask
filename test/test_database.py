from uuid import uuid4

import faker
import pytest

from database.model import Board, Priority, Status, Task, User
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

    assert user.name == fake_user["name"]
    assert user.email == fake_user["email"]
    assert user.password_hash == fake_user["password_hash"]


@pytest.mark.asyncio
async def test_board(fake: faker.Faker, session_manager: SessionManager):
    title = fake.name()
    async with session_manager.session_scope() as session:
        board = Board(title=title)
        session.add(board)
        await session.commit()
        await session.refresh(board)

    assert board.title == title


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

    assert task.title == fake_tasc["title"]
    assert task.description == fake_tasc["description"]
    assert task.deadline == fake_tasc["deadline"]
    assert task.priority == fake_tasc["priority"]
    assert task.status == fake_tasc["status"]
