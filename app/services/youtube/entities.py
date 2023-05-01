from dataclasses import dataclass


@dataclass(frozen=True)
class Video:
    id: str
    channel_id: str
    title: str


@dataclass(frozen=True)
class Subtitle:
    text: str
    start: float
    duration: float
    language: str
    video_id: str
