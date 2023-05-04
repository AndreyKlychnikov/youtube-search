from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.container import Container
from app.core.config import settings
from app.tasks.main import celery_app

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

celery_app.conf.beat_schedule  # noqa


@app.get("/run-async-task")
async def run_async_task():
    from app.tasks.async_tasks import example_async_task

    example_async_task.delay()
    return {"message": "Asynchronous task has been scheduled."}


@app.on_event("shutdown")
async def app_shutdown():
    await Container().search_service.close()
