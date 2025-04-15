from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger

from .settings import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")


def setup_global_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(
            "HTTPException occurred: status_code=%s, detail=%s, path=%s, client=%s",
            exc.status_code,
            exc.detail,
            request.url.path,
            request.client.host if request.client else "unknown",
        )
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP error occurred", "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled Exception: type=%s, path=%s, client=%s, detail=%s",
            type(exc).__name__,
            request.url.path,
            request.client.host if request.client else "unknown",
            str(exc),
        )
        return ORJSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later.",
            },
        )


def create_app():
    app = FastAPI(
        title=config.project.name,
        version=config.project.version,
        description=config.project.description,
        responses=ORJSONResponse,
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
        minimum_size=1000,
    )
    return app
