import asyncio
import logging

from celery import shared_task

from app.container import get_container


@shared_task
def example_async_task():
    logging.info("This is an example asynchronous task.")


@shared_task
def index_channels_task(channels_urls: list[str]):
    container = get_container()
    asyncio.get_event_loop().run_until_complete(
        container.search_service.index_link(channels_urls[0])
    )
    return "ok"
