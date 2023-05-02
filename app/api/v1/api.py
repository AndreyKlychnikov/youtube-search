from fastapi import APIRouter

from app.api.v1.endpoints import channels, videos

api_router = APIRouter()

api_router.include_router(
    channels.router,
    prefix="/channels",
    tags=["channels"],
)
api_router.include_router(
    videos.router,
    prefix="/videos",
    tags=["videos"],
)
