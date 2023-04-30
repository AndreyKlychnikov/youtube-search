import logging

from celery import shared_task


@shared_task
def example_periodic_task():
    logging.info("This is an example periodic task that runs every minute.")
