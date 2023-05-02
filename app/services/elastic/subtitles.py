import json
import logging

from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.helpers import bulk

from app.core.config import settings
from app.services.youtube.entities import Subtitle as SubtitleEntity


def get_lang_analyzer_mapping():
    with open(
        settings.BASE_DIR / "fixtures/elastic/lang_code_to_analyzer.json"
    ) as file:
        return json.loads("\n".join(file.readlines()))


lang_to_analyzer_mapping = get_lang_analyzer_mapping()


def get_async_es():
    return AsyncElasticsearch([settings.ELASTICSEARCH_HOST])  # TODO: make singleton


def get_es():
    return Elasticsearch([settings.ELASTICSEARCH_HOST])  # TODO: make singleton


def get_index_name(lang: str):
    return f"subtitles_{lang}"


async def save_subtitles_to_es(subtitles: list[SubtitleEntity], channel_id: str):
    es = get_es()
    docs = []
    for subtitle in subtitles:
        index_name = get_index_name(subtitle.language)
        docs.append(
            {
                "_index": index_name,
                "video_id": subtitle.video_id,
                "start_time": subtitle.start,
                "duration": subtitle.duration,
                "text": subtitle.text,
                "channel_id": channel_id,
            }
        )
    bulk(es, docs)


async def search_within_subtitles(q, lang) -> list[dict]:
    es = get_async_es()
    query = {
        "query": {
            "match": {
                "text": {
                    "query": q,
                    "operator": "and"
                }
            }
        }
    }
    res = await es.search(index=get_index_name(lang), body=query)
    out = []
    for hit in res["hits"]["hits"]:
        out.append({
            "video_id": hit["_source"]["video_id"],
            "channel_id": hit["_source"]["channel_id"],
            "text": hit["_source"]["text"],
            "start_time": hit["_source"]["start_time"],
            "duration": hit["_source"]["duration"],
        })
    return out


def create_elastic_indices(analyzers: list[str] = None):
    if not analyzers:
        analyzers = ["english", "french", "german", "italian", "spanish", "russian"]
    es = get_es()

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
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=index_settings)
        else:
            logging.info(f"The index {index_name} already exists.")
