import faker
import pytest

from database.model import User
from database.session import SessionManager


@pytest.mark.asyncio
async def test_user_db(fake: faker.Faker, session_manager: SessionManager):
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
