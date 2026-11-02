import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.config import settings

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app


@pytest.fixture
def test_engine():
    if not settings.test_database_url:
        raise ValueError("TEST_DATABASE_URL is required")

    url = make_url(settings.test_database_url)

    if url.database != "pastpaper_test":
        raise ValueError("Expected the dedicated pastpaper_test database")

    if url.database == make_url(settings.database_url).database:
        raise ValueError("Development and test databases must differ")

    engine = create_engine(url)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def client(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()

        TestSession = sessionmaker(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )

        def override_get_db():
            with TestSession() as db:
                yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            with TestClient(app) as test_client:
                yield test_client
        finally:
            app.dependency_overrides.pop(get_db, None)
            transaction.rollback()
