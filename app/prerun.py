import asyncio

from app.services.search.elastic.subtitles import ElasticSearchService


async def run():
    service = ElasticSearchService()
    await service.create_elastic_indices()
    await service.close()


if __name__ == "__main__":
    asyncio.run(run())
