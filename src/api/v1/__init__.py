from fastapi import APIRouter

from api.v1.auth.endpoint import router as auth_router
from api.v1.board.endpoint import router as board_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(board_router)
v1_router.include_router(auth_router)
