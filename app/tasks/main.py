from datetime import timedelta

from celery import Celery
from app.core.config import settings


celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.periodic_tasks", "app.tasks.async_tasks"],
)

celery_app.conf.task_routes = {
    "tasks.async_tasks.*": {"queue": "async_tasks"},
    "tasks.periodic_tasks.*": {"queue": "periodic_tasks"},
}

celery_app.conf.beat_schedule = {
    "example_periodic_task": {
        "task": "app.tasks.periodic_tasks.example_periodic_task",
        "schedule": timedelta(seconds=10),
    }
}

if __name__ == "__main__":
    celery_app.start()
