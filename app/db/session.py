from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    json_serializer=jsonable_encoder,
)
SessionLocal = sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


class SessionManager:
    def __init__(self):
        self.session = SessionLocal()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


async def dispose_engine():
    await engine.dispose()
