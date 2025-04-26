import asyncio

from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


class SessionManager:
    def __init__(self, database_url: str, **engine_kwargs: dict):
        self.engine = create_async_engine(
            database_url,
            future=True,
            **engine_kwargs,
        )
        self.session_local = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )
        self.scoped_session = async_scoped_session(
            self.session_local, scopefunc=asyncio.current_task
        )

    @asynccontextmanager
    async def session_scope(self):
        session = self.scoped_session()
        logger.debug(f"Session started: {session!r}")
        try:
            yield session
            await session.commit()
        except Exception:
            logger.exception(f"Error occurred, rolling back session: {session!r}")
            await session.rollback()
            raise
        finally:
            await session.close()
            self.scoped_session.remove()
            logger.debug(f"Session closed: {session!r}")

    async def dispose(self):
        await self.engine.dispose()
        logger.info("Engine disposed")

