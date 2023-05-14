import json
import logging
from abc import ABCMeta
from typing import Iterable

import dateutil.parser
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionManager
from app.models.base import Subtitle, Video
from app.services.search.base import SearchService, SingletonMeta
from app.services.youtube.entities import Subtitle as SubtitleEntity
from app.services.youtube.entities import Video as VideoEntity
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

    def _get_subtitles_index_name(self, lang: str):
        return f"subtitles_{self.lang_to_analyzer_mapping[lang]}"

    async def save_subtitles(
        self, subtitles: list[SubtitleEntity], channel_id: str, category_id
    ):
        docs = [
            {
                "_index": self._get_subtitles_index_name(subtitle.language),
                "video_id": subtitle.video_id,
                "start_time": subtitle.start,
                "duration": subtitle.duration,
                "text": subtitle.text,
                "channel_id": channel_id,
                "category_id": category_id,
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

    async def search_within_subtitles(
        self, q, lang, youtube_categories: list[str] = None
    ) -> list[dict]:
        match_stmt = {"match": {"text": {"query": q, "operator": "and"}}}
        if not youtube_categories:
            query = {"query": match_stmt}
        else:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            match_stmt,
                            {"terms": {"category_id": youtube_categories}},
                        ],
                    }
                }
            }
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
                    "category_id": {"type": "keyword"},
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
                logging.info("The index %s already exists.", index_name)

    async def _check_indexed(self, video: VideoEntity) -> bool:
        async with SessionManager() as db:
            result = await db.scalars(select(Video).where(Video.id == video.id))
            return result.first()

    async def _mark_indexed(self, videos: list[VideoEntity]):
        async with SessionManager() as db:
            db.add_all(
                [
                    Video(
                        id=video.id,
                        channel_id=video.channel_id,
                        title=video.title,
                        published_at=dateutil.parser.isoparse(video.published_at),
                        category_id=video.category_id,
                    )
                    for video in videos
                ]
            )
            await db.commit()

    async def _get_video_subtitles(
        self, video_id: str, lang: str = "en"
    ) -> list[Subtitle]:
        return get_video_subtitles(video_id, lang)
