import json
import logging
from abc import ABCMeta
from typing import Iterable

import dateutil.parser
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.base import Video as VideoModel
from app.services.search.base import SearchService, SingletonMeta
from app.services.youtube.entities import Subtitle
from app.services.youtube.entities import Subtitle as SubtitleEntity
from app.services.youtube.entities import Video
from app.services.youtube.videos import get_video_subtitles


class ElasticSearchMeta(SingletonMeta, ABCMeta):
    pass


class ElasticSearchService(SearchService, metaclass=ElasticSearchMeta):
    def __init__(self):
        self.lang_to_analyzer_mapping = self._get_lang_analyzer_mapping()
        self.async_es = self._get_async_es()

    @staticmethod
    def _get_lang_analyzer_mapping():
        file_path = settings.BASE_DIR / "fixtures/elastic/lang_code_to_analyzer.json"
        return json.loads(file_path.read_text())

    @staticmethod
    def _get_async_es():
        return AsyncElasticsearch([settings.ELASTICSEARCH_HOST])

    async def close(self):
        await self.async_es.close()

    @staticmethod
    def _get_subtitles_index_name(lang: str):
        return f"subtitles_{lang}"

    async def save_subtitles(self, subtitles: list[SubtitleEntity], channel_id: str):
        docs = [
            {
                "_index": self._get_subtitles_index_name(subtitle.language),
                "video_id": subtitle.video_id,
                "start_time": subtitle.start,
                "duration": subtitle.duration,
                "text": subtitle.text,
                "channel_id": channel_id,
            }
            for subtitle in subtitles
        ]
        await async_bulk(self.async_es, docs)

    @staticmethod
    def _format_search_result(hit):
        return {
            "video_id": hit["_source"]["video_id"],
            "channel_id": hit["_source"]["channel_id"],
            "text": hit["_source"]["text"],
            "start_time": hit["_source"]["start_time"],
            "duration": hit["_source"]["duration"],
        }

    async def search_within_subtitles(self, q, lang) -> list[dict]:
        query = {"query": {"match": {"text": {"query": q, "operator": "and"}}}}
        res = await self.async_es.search(
            index=self._get_subtitles_index_name(lang), body=query
        )
        return [self._format_search_result(hit) for hit in res["hits"]["hits"]]

    async def create_elastic_indices(self, analyzers: Iterable[str] = None):
        if not analyzers:
            analyzers = ("english", "french", "german", "italian", "spanish", "russian")

        index_settings = {
            "mappings": {
                "properties": {
                    "video_id": {"type": "keyword"},
                    "channel_id": {"type": "keyword"},
                    "start_time": {"type": "float"},
                    "duration": {"type": "float"},
                    "text": {"type": "text", "analyzer": ""},
                }
            }
        }

        for analyzer in analyzers:
            index_settings["mappings"]["properties"]["text"]["analyzer"] = analyzer

            index_name = f"subtitles_{analyzer}"
            if not await self.async_es.indices.exists(index=index_name):
                await self.async_es.indices.create(
                    index=index_name, body=index_settings
                )
            else:
                logging.info(f"The index {index_name} already exists.")

    async def _check_indexed(self, video: Video) -> bool:
        async with SessionLocal() as db:
            # db: AsyncSession
            result = await db.scalars(
                select(VideoModel).where(VideoModel.id == video.id)
            )
            return result.first()

    async def _mark_indexed(self, videos: list[Video]):
        async with SessionLocal() as db:
            db.add_all(
                [
                    VideoModel(
                        id=video.id,
                        channel_id=video.channel_id,
                        title=video.title,
                        published_at=dateutil.parser.isoparse(video.published_at),
                    )
                    for video in videos
                ]
            )
            await db.commit()

    async def _get_video_subtitles(
        self, video_id: str, lang: str = "en"
    ) -> list[Subtitle]:
        return get_video_subtitles(video_id, lang)
