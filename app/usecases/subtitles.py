import logging

import dateutil.parser
from sqlalchemy import desc, select
from sqlalchemy.orm import load_only

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.base import Subtitle, Video
from app.services.elastic.subtitles import save_subtitles_to_es
from app.services.youtube.entities import Subtitle as SubtitleEntity
from app.services.youtube.entities import Video as VideoEntity
from app.services.youtube.videos import (
    get_channel_id,
    get_channel_videos,
    get_video_subtitles,
)


async def save_videos_to_db(videos: list[VideoEntity]):
    async with SessionLocal() as db:
        db.add_all(
            [
                Video(
                    id=video.id,
                    channel_id=video.channel_id,
                    title=video.title,
                    published_at=dateutil.parser.isoparse(video.published_at),
                )
                for video in videos
            ]
        )
        await db.commit()


async def save_subtitles_to_db(subtitles: list[SubtitleEntity], *args):
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
    return (get_channel_id(url) for url in channel_urls)


async def get_channel_latest_video(channel_id) -> Video:
    async with SessionLocal() as db:
        videos = await db.scalars(
            select(Video)
            .where(Video.channel_id == channel_id)
            .order_by(desc(Video.published_at))
        )
        return videos.first()


async def get_channel_video_ids(channel_id) -> list[str]:
    async with SessionLocal() as db:
        videos = await db.scalars(
            select(Video)
            .where(Video.channel_id == channel_id)
            .options(load_only(Video.id))
        )
        return [video.id for video in videos]


async def index_channels(
    channel_urls: list[str],
    save_videos=save_videos_to_db,
    save_subtitles=save_subtitles_to_es,
):
    channel_ids = get_channel_ids(channel_urls)
    for channel_id in channel_ids:
        loaded_video_ids = set(await get_channel_video_ids(channel_id))
        logging.debug("loaded_video_ids: %s", loaded_video_ids)
        videos = get_channel_videos(channel_id, settings.YOUTUBE_API_KEY)
        saved_videos = []
        for video in videos:
            if video.id in loaded_video_ids:
                logging.debug("Skip video %s", video.id)
                continue
            subtitles = get_video_subtitles(video.id)
            try:
                await save_subtitles(subtitles, channel_id)
                saved_videos.append(video)
            except Exception as e:
                await save_videos(saved_videos)
                raise e
        logging.debug("Saving videos %d", len(saved_videos))
        await save_videos(saved_videos)
