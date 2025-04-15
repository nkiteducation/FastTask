import uvicorn

from core.app import create_app
from core.logger import logger_init
from core.settings import config
from api import api_router

logger_init()
app = create_app()
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.uvicorn.host,
        port=config.uvicorn.port,
        workers=config.uvicorn.workers,
    )
