from fastapi import APIRouter

from app.tasks.async_tasks import index_channels_task

router = APIRouter()


@router.post("/index")
def index(channel_urls: list[str]) -> str:
    return index_channels_task.delay(channel_urls)
