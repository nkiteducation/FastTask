import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from core.settings import config


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

    async def session_scope(self):
        session = self.scoped_session()
        logger.debug(f"Session started: {session}")
        try:
            yield session
            await session.commit()
        except Exception as exc:
            logger.exception(f"Session erorre: {exc}")
            await session.rollback()
            raise
        finally:
            await session.close()
            await self.scoped_session.remove()
            logger.debug(f"Session closed: {session}")

    async def dispose(self):
        await self.engine.dispose()
        logger.info("Engine disposed")


session_manager = SessionManager(
    database_url=config.database.URL.url,
    pool_size=config.database.poolSize,
    max_overflow=config.database.maxOverflow,
    pool_timeout=config.database.poolTimeout,
)
