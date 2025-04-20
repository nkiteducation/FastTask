from pathlib import Path
import sys

import pytest
import pytest_asyncio
from faker import Faker

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))


from database.session import SessionManager
from database.model import CoreModel


@pytest_asyncio.fixture(scope="session")
async def session_manager():
    test_session_manager = SessionManager(
        database_url="sqlite+aiosqlite:///test.db",
        connect_args={"check_same_thread": False},
    )
    yield test_session_manager
    await test_session_manager.dispose()


@pytest_asyncio.fixture(autouse=True, scope="module")
async def create_database(session_manager: SessionManager):
    async with session_manager.engine.begin() as conn:
        await conn.run_sync(CoreModel.metadata.create_all)
        yield
        await conn.run_sync(CoreModel.metadata.drop_all)


@pytest_asyncio.fixture
async def fake():
    return Faker("ru_RU")
