from dataclasses import dataclass


@dataclass(frozen=True)
class Video:
    id: str
    channel_id: str
    title: str
    published_at: str


@dataclass(frozen=True)
class Subtitle:
    text: str
    start: float
    duration: float
    language: str
    video_id: str
