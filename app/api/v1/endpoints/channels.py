from fastapi import APIRouter

from app.tasks.async_tasks import index_channels_task

router = APIRouter()


@router.post("/index")
def index(channel_urls: list[str]) -> str:
    result = index_channels_task.delay(channel_urls)
    return str(result)
