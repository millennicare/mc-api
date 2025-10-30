"""
Pytest configuration and shared fixtures for all tests.
"""

import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base
from src.main import app

# Initialize Faker for generating test data
fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create a test database engine using SQLite in-memory database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock database session for unit tests."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    session.scalars = AsyncMock()
    return session


@pytest.fixture
def mock_email_client() -> MagicMock:
    """Create a mock email client."""
    client = MagicMock()
    client.send_verification_email = MagicMock()
    client.send_password_reset_email = MagicMock()
    return client


@pytest.fixture
def mock_jwt_client() -> MagicMock:
    """Create a mock JWT client."""
    client = MagicMock()
    client.create_access_token = MagicMock(return_value="mock_access_token")
    client.create_refresh_token = MagicMock(return_value="mock_refresh_token")
    client.decode_access_token = MagicMock()
    client.decode_refresh_token = MagicMock()
    return client


@pytest.fixture
def sample_user_data() -> dict:
    """Generate sample user data for testing."""
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "email_verified": False,
        "created_at": fake.date_time(),
        "updated_at": fake.date_time(),
    }


@pytest.fixture
def sample_account_data() -> dict:
    """Generate sample account data for testing."""
    return {
        "id": fake.uuid4(),
        "account_id": "email",
        "provider_id": "credentials",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$test",  # hashed "password123"
        "user_id": fake.uuid4(),
        "created_at": fake.date_time(),
        "updated_at": fake.date_time(),
    }


@pytest.fixture
def sample_role_data() -> dict:
    """Generate sample role data for testing."""
    return {
        "id": fake.uuid4(),
        "name": "caregiver",
        "created_at": fake.date_time(),
        "updated_at": fake.date_time(),
    }


@pytest.fixture
def sample_session_data() -> dict:
    """Generate sample session data for testing."""
    return {
        "id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "expires_at": fake.future_datetime(),
        "created_at": fake.date_time(),
        "updated_at": fake.date_time(),
    }
