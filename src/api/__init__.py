from fastapi import APIRouter

from api.auth.router import router

from .v1 import v1_router

api_router = APIRouter()

api_router.include_router(router)
api_router.include_router(v1_router)
