import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.schemas.search_result import SearchResult
from app.services.youtube.entities import Subtitle
from app.services.youtube.entities import Subtitle as SubtitleEntity
from app.services.youtube.entities import Video
from app.services.youtube.videos import get_channel_videos, get_link_to_video


class LinkType(Enum):
    VIDEO_ID = 1
    CHANNEL_ID = 2


@dataclass(frozen=True)
class ResolvedLink:
    type: LinkType
    id: str


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SearchService(ABC):
    @abstractmethod
    async def search_within_subtitles(
        self, q, lang, youtube_categories: list[str] = None
    ) -> list[dict]:
        ...

    @abstractmethod
    async def save_subtitles(
        self, subtitles: list[SubtitleEntity], channel_id: str, category_id: str
    ):
        ...

    async def close(self):
        pass

    async def index_video(self, video: Video) -> bool:
        if await self._check_indexed(video):
            logging.debug("Skip video %s", video.id)
            return False
        subtitles = await self._get_video_subtitles(video.id)
        await self.save_subtitles(subtitles, video.channel_id, video.category_id)
        return True

    async def index_link(self, link):
        resolved_link = await self.resolve_link(link)
        if resolved_link.type == LinkType.CHANNEL_ID:
            return await self.index_channel(resolved_link.id)
        # TODO: index video

    async def index_channel(self, channel_id: str):
        videos = get_channel_videos(channel_id, settings.YOUTUBE_API_KEY)
        saved_videos = []
        for video in videos:
            if await self._check_indexed(video):
                logging.debug("Skip video %s", video.id)
                continue
            subtitles = await self._get_video_subtitles(video.id)
            try:
                await self.save_subtitles(subtitles, channel_id, video.category_id)
                saved_videos.append(video)
            except Exception as e:
                await self._mark_indexed(saved_videos)
                raise e
        logging.debug("Saving videos %d", len(saved_videos))
        await self._mark_indexed(saved_videos)

    async def search(
        self, q: str, lang: str = "en", youtube_categories: list[str] = None
    ):
        results = await self.search_within_subtitles(q, lang, youtube_categories)
        return [
            SearchResult(
                **result,
                url=get_link_to_video(
                    result["video_id"],
                    max(0, int(result["start_time"]) - 3),  # make bigger fragment
                )
            )
            for result in results
        ]

    async def resolve_link(self, link: str) -> ResolvedLink:
        return ResolvedLink(
            LinkType.CHANNEL_ID, self.get_channel_id(link)
        )  # TODO: add video links parsing

    @staticmethod
    def get_channel_id(link: str) -> str:  # TODO: make async
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        meta = soup.find("meta", itemprop="channelId")
        if not meta:
            raise ValueError
        return meta["content"]

    @abstractmethod
    async def _check_indexed(self, video: Video) -> bool:
        ...

    @abstractmethod
    async def _get_video_subtitles(
        self, video_id: str, lang: str = "en"
    ) -> list[Subtitle]:
        ...

    @abstractmethod
    async def _mark_indexed(self, videos: list[Video]):
        ...
