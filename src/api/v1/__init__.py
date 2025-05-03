from fastapi import APIRouter

from api.v1.auth.views import router as auth_router
from api.v1.user.views import router as user_router

v1_router = APIRouter()
v1_router.include_router(user_router)
v1_router.include_router(auth_router)
