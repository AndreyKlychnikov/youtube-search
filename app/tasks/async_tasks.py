import logging

from celery import shared_task


@shared_task
def example_async_task():
    logging.info("This is an example asynchronous task.")
