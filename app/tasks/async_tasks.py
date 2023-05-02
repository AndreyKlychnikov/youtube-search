import asyncio
import logging

from celery import shared_task

from app.usecases.subtitles import index_channels


@shared_task
def example_async_task():
    logging.info("This is an example asynchronous task.")


@shared_task
def index_channels_task(channels_urls: list[str]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(index_channels(channels_urls))
    return "ok"
