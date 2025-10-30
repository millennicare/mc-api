"""
Unit tests for UserRepository.
"""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import CreateUserSchema


@pytest.mark.unit
@pytest.mark.repository
class TestUserRepository:
    """Test suite for UserRepository."""

    @pytest.fixture
    def repository(self, mock_db_session: AsyncSession) -> UserRepository:
        """Create a UserRepository instance with a mock database session."""
        return UserRepository(db=mock_db_session)

    async def test_get_user_success(
        self,
        repository: UserRepository,
        mock_db_session: AsyncSession,
        sample_user_data: dict,
    ):
        """Test successfully retrieving a user by ID."""
        # Arrange
        user_id = sample_user_data["id"]
        mock_user = User(**sample_user_data)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user(user_id=user_id)

        # Assert
        assert result is not None
        assert result.id == user_id
        assert result.email == sample_user_data["email"]
        mock_db_session.execute.assert_called_once()

    async def test_get_user_not_found(
        self, repository: UserRepository, mock_db_session: AsyncSession
    ):
        """Test retrieving a non-existent user returns None."""
        # Arrange
        user_id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user(user_id=user_id)

        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()

    async def test_create_user_success(
        self,
        repository: UserRepository,
        mock_db_session: AsyncSession,
        sample_user_data: dict,
    ):
        """Test successfully creating a new user."""
        # Arrange
        create_schema = CreateUserSchema(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            email_verified=False,
        )
        mock_user = User(**sample_user_data)

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repository.create_user(values=create_schema)

        # Assert
        assert result is not None
        assert result.email == sample_user_data["email"]
        assert result.name == sample_user_data["name"]
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()

    async def test_get_user_by_email_success(
        self,
        repository: UserRepository,
        mock_db_session: AsyncSession,
        sample_user_data: dict,
    ):
        """Test successfully retrieving a user by email."""
        # Arrange
        email = sample_user_data["email"]
        mock_user = User(**sample_user_data)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user_by_email(email=email)

        # Assert
        assert result is not None
        assert result.email == email
        mock_db_session.execute.assert_called_once()

    async def test_get_user_by_email_not_found(
        self, repository: UserRepository, mock_db_session: AsyncSession
    ):
        """Test retrieving a user by non-existent email returns None."""
        # Arrange
        email = "nonexistent@example.com"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repository.get_user_by_email(email=email)

        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()

    async def test_delete_user(
        self, repository: UserRepository, mock_db_session: AsyncSession
    ):
        """Test deleting a user."""
        # Arrange
        user_id = str(uuid4())

        # Act
        await repository.delete_user(id=user_id)

        # Assert
        mock_db_session.execute.assert_called_once()

    async def test_get_users_with_pagination(
        self,
        repository: UserRepository,
        mock_db_session: AsyncSession,
        sample_user_data: dict,
    ):
        """Test retrieving users with pagination."""
        # Arrange
        skip = 0
        limit = 10
        mock_users = [User(**sample_user_data) for _ in range(3)]

        mock_result = MagicMock()
        mock_result.all.return_value = mock_users
        mock_db_session.scalars.return_value = mock_result

        # Act
        result = await repository.get_users(skip=skip, limit=limit)

        # Assert
        assert len(result) == 3
        mock_db_session.scalars.assert_called_once()

    async def test_update_user_success(
        self,
        repository: UserRepository,
        mock_db_session: AsyncSession,
        sample_user_data: dict,
    ):
        """Test successfully updating a user."""
        # Arrange
        user_id = uuid4()
        update_values = {"email_verified": True}
        updated_user_data = {**sample_user_data, **update_values}
        mock_user = User(**updated_user_data)

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repository.update_user(user_id=user_id, values=update_values)

        # Assert
        assert result is not None
        assert result.email_verified is True
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
