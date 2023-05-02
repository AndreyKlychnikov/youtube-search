from pydantic import BaseModel


class SearchResult(BaseModel):
    video_id: str
    channel_id: str
    text: str
    start_time: float
    duration: float
