from app.core.config import settings
from app.db.session import SessionLocal
from app.models.base import Video, Subtitle
from app.services.youtube.entities import Video as VideoEntity
from app.services.youtube.entities import Subtitle as SubtitleEntity
from app.services.youtube.videos import (
    get_channel_id,
    get_channel_videos,
    get_video_subtitles,
)


async def save_videos_to_db(videos: list[VideoEntity]):
    async with SessionLocal() as db:
        db.add_all(
            [
                Video(id=video.id, channel_id=video.channel_id, title=video.title)
                for video in videos
            ]
        )
    db.commit()


async def save_subtitles_to_db(subtitles: list[SubtitleEntity]):
    async with SessionLocal() as db:
        db.add_all(
            [
                Subtitle(
                    video_id=sub.video_id,
                    start_time=sub.start,
                    end_time=sub.start + sub.duration,
                    text=sub.text,
                )
                for sub in subtitles
            ]
        )
    db.commit()


def get_channel_ids(channel_urls: list[str]):
    return [get_channel_id(url) for url in channel_urls]


async def index_channels(
    channel_urls: list[str],
    save_videos=save_videos_to_db,
    save_subtitles=save_subtitles_to_db,
):
    channel_ids = get_channel_ids(channel_urls)
    videos = []
    subtitles = []
    for channel_id in channel_ids:
        videos_ = get_channel_videos(channel_id, settings.YOUTUBE_API_KEY)
        for video in videos_:
            subtitles_ = get_video_subtitles(video.id)
            subtitles.extend(subtitles_)
        videos.extend(videos_)
    await save_videos(videos)
    await save_subtitles(subtitles)
