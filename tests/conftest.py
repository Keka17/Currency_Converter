import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.main import app
from app.database.database import get_db_connection
from app.database.models import Base
from app.core.config import get_settings

settings = get_settings()

TEST_DATABASE_URL = settings.TEST_DATABASE_URL


@pytest.fixture(scope="session")
async def async_db_engine():
    """Drop all database every time when test complete."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def async_session(async_db_engine):
    """Create a fresh session for each test"""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(bind=connection, expire_on_commit=False) as session:
            yield session

            await transaction.rollback()


@pytest.fixture
async def client(async_session):
    """Replaces the db dependency."""

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db_connection] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
