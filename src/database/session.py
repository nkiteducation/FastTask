import asyncio

from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


class SessionManager:
    def __init__(
        self, database_url: str, pool_size: int, max_overflow: int, pool_timeout: int
    ):
        self.engine = create_async_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            future=True,
        )
        self.session_local = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )
        self.session = async_scoped_session(
            self.session_local, scopefunc=asyncio.current_task
        )

    @asynccontextmanager
    async def session_scope(self):
        session = self.session()
        self.session.session_factory
        try:
            logger.debug("Session scope started")
            yield session
            logger.debug("Session scope completed successfully")
        except Exception as e:
            await session.rollback()
            logger.error("Session scope encountered an error: {}", e, exc_info=True)
            raise e
        finally:
            await session.close()
            await self.session.remove()
            logger.debug("Session scope closed and session removed")

    async def dispose(self):
        await self.engine.dispose()
        logger.info("Engine disposed")
