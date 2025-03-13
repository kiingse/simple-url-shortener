from typing import AsyncGenerator, Dict, Generator, Tuple
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from app.common.db import Base
from app.main import app
from app.models import URLMapping
from app.url.repositories import AsyncURLMappingRepository
from app.url.services.url_service import URLMappingService

postgres = PostgresContainer("postgres:16-alpine", dbname="test")


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def db_container() -> Generator[PostgresContainer, None, None]:
    postgres.start()
    yield postgres
    postgres.stop()


@pytest_asyncio.fixture(scope="session")
async def async_db_engine(
    db_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    connection_url = db_container.get_connection_url().replace(
        "postgresql+psycopg2", "postgresql+asyncpg"
    )
    engine = create_async_engine(connection_url, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_db_session(
    async_db_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async_session = async_sessionmaker(async_db_engine, expire_on_commit=True)
    yield async_session


@pytest.fixture(scope="module")
def db_engine(db_container: PostgresContainer) -> Generator[Engine, None, None]:
    connection_url = db_container.get_connection_url()
    engine = create_engine(connection_url)
    with engine.begin() as conn:
        Base.metadata.create_all(conn)

    yield engine

    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
    engine.dispose()


@pytest.fixture(scope="module")
def db_session(sync_db_engine) -> Generator[sessionmaker[Session], None, None]:
    session = sessionmaker(sync_db_engine)
    yield session


@pytest_asyncio.fixture(scope="function")
async def repository(async_db_session: async_sessionmaker[AsyncSession]):
    return AsyncURLMappingRepository(async_db_session)


@pytest.fixture(scope="session")
def mock_url_repository() -> AsyncMock:
    return AsyncMock(spec=AsyncURLMappingRepository)


@pytest.fixture
def service(mock_url_repository):
    return URLMappingService(url_repository=mock_url_repository)


@pytest.fixture
def mock_url_service():
    with patch("app.url.services.URLMappingService") as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest_asyncio.fixture(scope="function")
async def clean_db(async_db_engine):
    async with async_db_engine.begin() as conn:
        await conn.execute(URLMapping.__table__.delete())  # type: ignore
    yield


@pytest_asyncio.fixture(scope="function")
async def sample_url_mappings(
    async_db_session: async_sessionmaker[AsyncSession], clean_db
):
    async with async_db_session() as session:
        url_mappings = [
            URLMapping(original_url="https://example.com", short_code="abc123"),
            URLMapping(original_url="https://test.com", short_code="def456"),
            URLMapping(original_url="https://another.com", short_code="ghi789"),
        ]
        for mapping in url_mappings:
            session.add(mapping)
        await session.commit()

        for mapping in url_mappings:
            await session.refresh(mapping)

    return url_mappings


# SETUP FOR INCREMENTAL TESTING
# store history of failures per test class name and per index in parametrize
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed
            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the first test function to fail for this class name
            # and index
            test_name = _test_failed_incremental[cls_name].get(parametrize_index, None)
            # if name found, test has failed for the combination of class name & test
            # name
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))
