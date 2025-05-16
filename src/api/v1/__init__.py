from fastapi import APIRouter, Depends

from api.v1.auth.dependencies import verification_access_jwt
from api.v1.auth.endpoint import router as auth_router
from api.v1.board.endpoint import router as board_router

v1_router = APIRouter(prefix="/v1")
secured_router = APIRouter(dependencies=[Depends(verification_access_jwt)])

secured_router.include_router(board_router)
v1_router.include_router(auth_router)
v1_router.include_router(secured_router)
