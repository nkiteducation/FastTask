import pytest
import pytest_asyncio
from database.session import SessionManager
import faker
from database.model import Role, Priority, Status, User, Task


@pytest.fixture
def fake_user(fake: faker.Faker):
    return {
        "name": fake.name(),
        "email": fake.email(),
        "password_hesh": fake.password(),
        "role": fake.enum(Role),
    }


@pytest.fixture
def fake_task(fake: faker.Faker):
    return {
        "title": fake.sentence(nb_words=6).rstrip("."),
        "description": fake.paragraph(nb_sentences=3),
        "deadline": fake.date_time_between(start_date="now", end_date="+30d"),
        "priority": fake.enum(Priority),
        "status": fake.enum(Status),
    }


@pytest.mark.asyncio
async def test_user(fake_user, session_manager: SessionManager):
    async with session_manager.session_scope() as session:
        user = User(**fake_user)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    assert user.name == fake_user["name"]
    assert user.email == fake_user["email"]
    assert user.password_hesh == fake_user["password_hesh"]
    assert user.role == fake_user["role"]


@pytest.mark.asyncio
async def test_task(fake_task, session_manager: SessionManager):
    async with session_manager.session_scope() as session:
        task = Task(**fake_task)
        session.add(task)
        await session.commit()
        await session.refresh(task)

    assert task.title == fake_task["title"]
    assert task.description == fake_task["description"]
    assert task.deadline == fake_task["deadline"]
    assert task.priority == fake_task["priority"]
    assert task.status == fake_task["status"]


@pytest.mark.asyncio
async def test_user_tasks(fake_user, fake_task, session_manager: SessionManager):
    user = User(**fake_user)

    for _ in range(10):
        user.tasks.append(Task(**fake_task))

    async with session_manager.session_scope() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        rows = [t for t in await user.awaitable_attrs.tasks]

    assert 10 == len(rows)
