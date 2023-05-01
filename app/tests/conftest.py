import asyncio
from typing import Generator

import pytest
import pytest_asyncio
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
TestingSessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def db():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = TestingSessionLocal(bind=connection)

        # Begin a nested transaction (using SAVEPOINT).
        nested = (await connection.begin_nested()).sync_transaction

        # If the application code calls session.commit, it will end the nested
        # transaction. Need to start a new one when that happens.
        @sa.event.listens_for(session.sync_session, "after_transaction_end")  # noqa
        async def end_savepoint(session_, transaction_):
            nonlocal nested
            if not nested.is_active:
                nested = await connection.sync_connection.begin_nested()

        yield session

        # Rollback the overall transaction, restoring the state before the test ran.
        await session.close()
        await transaction.rollback()
        await connection.rollback()


@pytest_asyncio.fixture
async def test_app(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield app
    del app.dependency_overrides[get_db]
