from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger

from core.settings import config
from database.model import CoreModel
from database.session import session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with session_manager.engine.begin() as conn:
        await conn.run_sync(CoreModel.metadata.create_all)
    logger.info("Starting up application...")
    yield
    logger.info("Shutting down application...")
    await session_manager.dispose()


def setup_global_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error occurred: {exc}")
        return ORJSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )


def create_app():
    app = FastAPI(
        title=config.project.name,
        version=config.project.version,
        description=config.project.description,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    setup_global_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        GZipMiddleware,
        minimum_size=400,
    )

    return app
