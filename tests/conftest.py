import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import get_db_connection

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.models import Base

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables once for the entire test session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Replaces the db dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session will be closed by the db_session fixture

    app.dependency_overrides[get_db_connection] = override_get_db
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
