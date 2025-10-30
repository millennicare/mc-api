"""
Unit tests for AuthService.
"""

from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from argon2 import PasswordHasher
from fastapi import HTTPException

from src.models.account import Account
from src.models.role import Role
from src.models.session import Session
from src.models.user import User
from src.models.verification_code import VerificationCodeEnum
from src.repositories.account_repository import AccountRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.user_to_role_repository import UserToRoleRepository
from src.repositories.verification_code_repository import VerificationCodeRepository
from src.schemas.auth_schemas import SignUpSchema
from src.services.auth_service import AuthService


@pytest.mark.unit
@pytest.mark.service
@pytest.mark.auth
class TestAuthService:
    """Test suite for AuthService."""

    @pytest.fixture
    def mock_account_repository(self) -> MagicMock:
        """Create a mock AccountRepository."""
        return MagicMock(spec=AccountRepository)

    @pytest.fixture
    def mock_role_repository(self) -> MagicMock:
        """Create a mock RoleRepository."""
        return MagicMock(spec=RoleRepository)

    @pytest.fixture
    def mock_session_repository(self) -> MagicMock:
        """Create a mock SessionRepository."""
        return MagicMock(spec=SessionRepository)

    @pytest.fixture
    def mock_user_repository(self) -> MagicMock:
        """Create a mock UserRepository."""
        return MagicMock(spec=UserRepository)

    @pytest.fixture
    def mock_user_to_role_repository(self) -> MagicMock:
        """Create a mock UserToRoleRepository."""
        return MagicMock(spec=UserToRoleRepository)

    @pytest.fixture
    def mock_verification_code_repository(self) -> MagicMock:
        """Create a mock VerificationCodeRepository."""
        return MagicMock(spec=VerificationCodeRepository)

    @pytest.fixture
    def auth_service(
        self,
        mock_account_repository: MagicMock,
        mock_role_repository: MagicMock,
        mock_session_repository: MagicMock,
        mock_user_repository: MagicMock,
        mock_user_to_role_repository: MagicMock,
        mock_verification_code_repository: MagicMock,
        mock_email_client: MagicMock,
        mock_jwt_client: MagicMock,
    ) -> AuthService:
        """Create an AuthService instance with mocked dependencies."""
        return AuthService(
            account_repository=mock_account_repository,
            role_repository=mock_role_repository,
            session_repository=mock_session_repository,
            user_repository=mock_user_repository,
            user_to_role_repository=mock_user_to_role_repository,
            verification_code_repository=mock_verification_code_repository,
            email_client=mock_email_client,
            jwt_client=mock_jwt_client,
        )

    async def test_sign_up_success(
        self,
        auth_service: AuthService,
        mock_user_repository: MagicMock,
        mock_account_repository: MagicMock,
        mock_role_repository: MagicMock,
        mock_user_to_role_repository: MagicMock,
        sample_user_data: dict,
        sample_role_data: dict,
    ):
        """Test successful user sign up."""
        # Arrange
        sign_up_data = SignUpSchema(
            name="John Doe",
            email="john@example.com",
            password="SecurePass123!",
            roles=["caregiver"],
        )

        mock_user = User(**sample_user_data)
        mock_role = Role(**sample_role_data)

        mock_user_repository.get_user_by_email = AsyncMock(return_value=None)
        mock_user_repository.create_user = AsyncMock(return_value=mock_user)
        mock_account_repository.create_account = AsyncMock()
        mock_role_repository.get_role_by_name = AsyncMock(return_value=mock_role)
        mock_user_to_role_repository.create_user_to_role = AsyncMock()

        # Act
        result = await auth_service.sign_up(body=sign_up_data)

        # Assert
        assert result is not None
        assert result.email == mock_user.email
        mock_user_repository.get_user_by_email.assert_called_once_with(
            email=sign_up_data.email
        )
        mock_user_repository.create_user.assert_called_once()
        mock_account_repository.create_account.assert_called_once()
        mock_role_repository.get_role_by_name.assert_called_once_with(name="caregiver")
        mock_user_to_role_repository.create_user_to_role.assert_called_once()

    async def test_sign_up_user_already_exists(
        self,
        auth_service: AuthService,
        mock_user_repository: MagicMock,
        sample_user_data: dict,
    ):
        """Test sign up fails when user already exists."""
        # Arrange
        sign_up_data = SignUpSchema(
            name="John Doe",
            email="existing@example.com",
            password="SecurePass123!",
            roles=["caregiver"],
        )

        existing_user = User(**sample_user_data)
        mock_user_repository.get_user_by_email = AsyncMock(return_value=existing_user)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.sign_up(body=sign_up_data)

        assert exc_info.value.status_code == HTTPStatus.CONFLICT
        assert "already exists" in exc_info.value.detail

    async def test_sign_in_success(
        self,
        auth_service: AuthService,
        mock_user_repository: MagicMock,
        mock_account_repository: MagicMock,
        mock_role_repository: MagicMock,
        mock_session_repository: MagicMock,
        sample_user_data: dict,
        sample_account_data: dict,
        sample_role_data: dict,
        sample_session_data: dict,
    ):
        """Test successful user sign in."""
        # Arrange
        email = "test@example.com"
        password = "password123"

        user_data = {**sample_user_data, "email_verified": True}
        mock_user = User(**user_data)
        mock_account = Account(**sample_account_data)
        mock_role = Role(**sample_role_data)
        mock_session = Session(**sample_session_data)

        mock_user_repository.get_user_by_email = AsyncMock(return_value=mock_user)
        mock_account_repository.get_accounts_by_user_id = AsyncMock(
            return_value=[mock_account]
        )
        mock_role_repository.get_roles_by_user_id = AsyncMock(return_value=[mock_role])
        mock_session_repository.create_session = AsyncMock(return_value=mock_session)

        # Mock password validation
        with patch.object(auth_service, "_validate_password", return_value=True):
            # Act
            result = await auth_service.sign_in(email=email, password=password)

        # Assert
        assert result is not None
        assert result.access_token == "mock_access_token"
        assert result.refresh_token == "mock_refresh_token"
        mock_user_repository.get_user_by_email.assert_called_once_with(email=email)
        mock_session_repository.create_session.assert_called_once()

    async def test_sign_in_user_not_found(
        self,
        auth_service: AuthService,
        mock_user_repository: MagicMock,
    ):
        """Test sign in fails when user doesn't exist."""
        # Arrange
        email = "nonexistent@example.com"
        password = "password123"

        mock_user_repository.get_user_by_email = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.sign_in(email=email, password=password)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert "Incorrect email or password" in exc_info.value.detail

    async def test_sign_in_incorrect_password(
        self,
        auth_service: AuthService,
        mock_user_repository: MagicMock,
        mock_account_repository: MagicMock,
        sample_user_data: dict,
        sample_account_data: dict,
    ):
        """Test sign in fails with incorrect password."""
        # Arrange
        email = "test@example.com"
        password = "wrongpassword"

        user_data = {**sample_user_data, "email_verified": True}
        mock_user = User(**user_data)
        mock_account = Account(**sample_account_data)

        mock_user_repository.get_user_by_email = AsyncMock(return_value=mock_user)
        mock_account_repository.get_accounts_by_user_id = AsyncMock(
            return_value=[mock_account]
        )

        # Mock password validation to raise VerifyMismatchError (the actual exception from argon2)
        from argon2.exceptions import VerifyMismatchError

        with patch.object(
            auth_service, "_validate_password", side_effect=VerifyMismatchError()
        ):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.sign_in(email=email, password=password)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED

    async def test_verify_email_success(
        self,
        auth_service: AuthService,
        mock_verification_code_repository: MagicMock,
        mock_user_repository: MagicMock,
    ):
        """Test successful email verification."""
        # Arrange
        user_id = "test-user-id"
        code = "123456"

        mock_verification_code = MagicMock()
        mock_verification_code.identifier = VerificationCodeEnum.VERIFY_EMAIL
        mock_verification_code.value = code
        mock_verification_code.expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=15
        )

        mock_verification_code_repository.get_verification_code = AsyncMock(
            return_value=mock_verification_code
        )
        mock_verification_code_repository.delete_verification_code = AsyncMock()
        mock_user_repository.update_user = AsyncMock()

        # Act
        await auth_service.verify_email(code=code, user_id=user_id)

        # Assert
        mock_verification_code_repository.get_verification_code.assert_called_once_with(
            user_id=user_id
        )
        mock_verification_code_repository.delete_verification_code.assert_called_once()
        mock_user_repository.update_user.assert_called_once_with(
            user_id=user_id, values={"email_verified": True}
        )

    async def test_verify_email_invalid_code(
        self,
        auth_service: AuthService,
        mock_verification_code_repository: MagicMock,
    ):
        """Test email verification fails with invalid code."""
        # Arrange
        user_id = "test-user-id"
        code = "123456"

        mock_verification_code_repository.get_verification_code = AsyncMock(
            return_value=None
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.verify_email(code=code, user_id=user_id)

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert "invalid or expired" in exc_info.value.detail

    async def test_sign_out(
        self,
        auth_service: AuthService,
        mock_session_repository: MagicMock,
    ):
        """Test user sign out."""
        # Arrange
        session_id = "test-session-id"
        mock_session_repository.delete_session = AsyncMock()

        # Act
        await auth_service.sign_out(session_id=session_id)

        # Assert
        mock_session_repository.delete_session.assert_called_once_with(
            session_id=session_id
        )

    async def test_forgot_password_user_not_found(
        self,
        auth_service: AuthService,
        mock_user_repository: MagicMock,
    ):
        """Test forgot password with non-existent user (should not reveal user doesn't exist)."""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repository.get_user_by_email = AsyncMock(return_value=None)

        # Act
        result = await auth_service.forgot_password(email=email)

        # Assert - should return None without error
        assert result is None
        mock_user_repository.get_user_by_email.assert_called_once_with(email=email)

    def test_generate_verification_code(self, auth_service: AuthService):
        """Test verification code generation."""
        # Act
        code = auth_service._generate_verification_code()

        # Assert
        assert len(code) == 6
        assert code.isdigit()
        assert 100000 <= int(code) <= 999999

    def test_hash_password(self, auth_service: AuthService):
        """Test password hashing."""
        # Arrange
        password = "SecurePassword123!"

        # Act
        hashed = auth_service._hash_password(password)

        # Assert
        assert hashed != password
        assert hashed.startswith("$argon2")

        # Verify the hash can be validated
        ph = PasswordHasher()
        assert ph.verify(hashed, password)
