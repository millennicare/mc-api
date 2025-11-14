import random
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Literal
from urllib.parse import urlencode
from uuid import UUID

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException

from src.clients.cache import CacheClient
from src.clients.email import EmailClient
from src.clients.token import JWTClient
from src.core.config import base_settings, google_oauth_settings
from src.core.constants import (
    GOOGLE_AUTH_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL,
    SESSION_EXPIRE_DAYS,
    VERIFICATION_CODE_EXPIRE_MINUTES,
)
from src.core.logger import setup_logger
from src.models.account import Account
from src.models.user import User
from src.models.verification_code import VerificationCodeEnum
from src.repositories.account_repository import AccountRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.user_info_repository import UserInfoRepository
from src.repositories.user_repository import UserRepository
from src.repositories.user_to_role_repository import UserToRoleRepository
from src.repositories.verification_code_repository import VerificationCodeRepository
from src.schemas.account_schemas import CreateAccountSchema, UpdateAccountSchema
from src.schemas.auth_schemas import (
    ResetPasswordSchema,
    RoleEnum,
    SignUpSchema,
    TokenResponse,
)
from src.schemas.session_schemas import CreateSessionSchema
from src.schemas.user_schemas import (
    CreateUserSchema,
    UpdateUserSchema,
    UserSchema,
    UserWithInformationSchema,
)
from src.schemas.verification_code_schemas import CreateVerificationCodeSchema


class AuthService:
    def __init__(
        self,
        account_repository: AccountRepository,
        role_repository: RoleRepository,
        session_repository: SessionRepository,
        user_info_repository: UserInfoRepository,
        user_repository: UserRepository,
        user_to_role_repository: UserToRoleRepository,
        verification_code_repository: VerificationCodeRepository,
        email_client: EmailClient,
        jwt_client: JWTClient,
        cache_client: CacheClient,
    ):
        self.account_repository = account_repository
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.session_repository = session_repository
        self.user_info_repository = user_info_repository
        self.user_to_role_repository = user_to_role_repository
        self.verification_code_repository = verification_code_repository
        self.email_client = email_client
        self.jwt_client = jwt_client
        self.cache_client = cache_client
        self.logger = setup_logger(__name__)
        self.password_hasher = PasswordHasher()

    # ===== Public Methods =====

    async def sign_up(self, body: SignUpSchema) -> UserSchema:
        """Register a new user with email/password"""
        # Check for existing user
        existing_user = await self.user_repository.get_user_by_email(email=body.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A user with this email address already exists",
            )

        # Create user
        user = await self.user_repository.create_user(
            values=CreateUserSchema.model_validate(
                {
                    "first_name": body.first_name,
                    "last_name": body.last_name,
                    "email": body.email,
                    "email_verified": False,
                }
            )
        )
        self.logger.info(f"Created user {body.email}")

        # Create credentials account
        await self.account_repository.create_account(
            CreateAccountSchema(
                account_id="email",
                provider_id="credentials",
                password=self.password_hasher.hash(body.password),
                user_id=user.id,
            )
        )

        # Assign roles
        await self._assign_roles_to_user(user.id, body.roles)

        # Send verification email
        await self._send_verification_email(user)

        return UserSchema.model_validate(user)

    async def sign_in(self, email: str, password: str) -> TokenResponse:
        """Authenticate user with email/password"""
        # Get user or throw
        user = await self._get_user_or_404(
            email=email, error_message="Incorrect email or password"
        )

        account = await self._get_credentials_account(user_id=user.id)
        if not account or not account.password:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        self._verify_password(account.password, password)

        # Generate tokens
        return await self._create_user_session(user.id)

    async def verify_email(self, token: str, code: str) -> None:
        """Verify user's email with token and code"""
        verification_code = await self._get_verification_code_or_404(
            token=token,
            expected_type=VerificationCodeEnum.VERIFY_EMAIL,
        )

        # Validate code
        if verification_code.value != code:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Verification code is incorrect",
            )

        # Check expiration
        self._check_verification_code_expiry(verification_code)

        # Mark email as verified
        await self.user_repository.update_user(
            user_id=verification_code.user_id,
            values=UpdateUserSchema.model_validate({"email_verified": True}),
        )

        # Delete used verification code
        await self.verification_code_repository.delete_verification_code(
            user_id=verification_code.user_id,
            identifier=VerificationCodeEnum.VERIFY_EMAIL,
        )

        self.logger.info(f"User {verification_code.user_id} email verified")

    async def sign_out(self, session_id: UUID) -> None:
        """Sign out user by deleting their session"""
        await self.session_repository.delete_session(session_id=session_id)
        self.logger.info(f"Deleted session {session_id}")

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        # Decode and validate refresh token
        decoded = self.jwt_client.decode_refresh_token(refresh_token)
        user_id = UUID(decoded.sub)
        session_id = UUID(decoded.sessionId)

        # Verify session exists
        session = await self._get_session_or_404(session_id)

        # Extend session expiration
        await self.session_repository.update_session(
            session_id=session.id,
            values={
                "expires_at": datetime.now(timezone.utc)
                + timedelta(days=SESSION_EXPIRE_DAYS)
            },
        )

        # Get user roles
        roles = await self.role_repository.get_roles_by_user_id(user_id=user_id)

        # Generate new tokens
        access_token = self.jwt_client.create_access_token(
            user_id=user_id,
            session_id=session_id,
            roles=[role.name for role in roles],
        )
        refresh_token = self.jwt_client.create_refresh_token(
            user_id=user_id,
            session_id=session_id,
        )

        self.logger.info(f"Refreshed tokens for user {user_id}")
        return TokenResponse.model_validate(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

    async def forgot_password(self, email: str) -> None:
        """Initiate password reset flow"""
        # Get user (don't reveal if email exists for security)
        user = await self.user_repository.get_user_by_email(email=email)
        if not user:
            return

        # Check if user has credentials account
        account = await self._get_credentials_account(user.id)
        if not account:
            return

        # Delete existing reset codes
        await self.verification_code_repository.delete_verification_code(
            user_id=user.id,
            identifier=VerificationCodeEnum.FORGOT_PASSWORD,
        )

        # Create new reset code
        code = self._generate_verification_code()
        token = secrets.token_urlsafe(32)
        await self.verification_code_repository.create_verification_code(
            CreateVerificationCodeSchema(
                value=code,
                token=token,
                user_id=user.id,
                expires_at=datetime.now(timezone.utc)
                + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES),
                identifier=VerificationCodeEnum.FORGOT_PASSWORD,
            )
        )

        # Send reset email
        reset_url = f"{base_settings.base_url}/reset-password?token={token}"
        self.email_client.send_password_reset_email(email=user.email, link=reset_url)
        self.logger.info(f"Sent password reset email to {email}")

    async def reset_password(self, body: ResetPasswordSchema) -> None:
        """Reset password using verification token"""
        # Get and validate verification code
        verification_code = await self._get_verification_code_or_404(
            token=body.token,
            expected_type=VerificationCodeEnum.FORGOT_PASSWORD,
        )

        # Check expiration
        self._check_verification_code_expiry(verification_code)

        # Get credentials account
        account = await self._get_credentials_account_or_404(
            user_id=verification_code.user_id
        )

        # Update password
        hashed_password = self.password_hasher.hash(body.password)
        await self.account_repository.update_account(
            account_id=account.id,
            provider_id="credentials",
            values=UpdateAccountSchema(password=hashed_password),
        )

        # Delete used verification code
        await self.verification_code_repository.delete_verification_code(
            user_id=verification_code.user_id,
            identifier=VerificationCodeEnum.FORGOT_PASSWORD,
        )

        self.logger.info(f"Password reset for user {verification_code.user_id}")

    async def resend_verification(self, email: str) -> None:
        """Resend email verification code"""
        # Get user (don't reveal if email exists)
        user = await self.user_repository.get_user_by_email(email=email)
        if not user or user.email_verified:
            return

        # Delete existing verification codes
        await self.verification_code_repository.delete_verification_code(
            user_id=user.id,
            identifier=VerificationCodeEnum.VERIFY_EMAIL,
        )

        # Send new verification email
        await self._send_verification_email(user)
        self.logger.info(f"Resent verification email to {email}")

    async def get_me(self, user_id: UUID) -> UserWithInformationSchema:
        """Get current user information"""
        user = await self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="User not found",
            )
        return UserWithInformationSchema.model_validate(user)

    async def initiate_oauth_login(
        self,
        provider: Literal["google"],
        role: Literal["careseeker", "caregiver"],
    ) -> dict[str, str]:
        """Initiate OAuth2 flow with provider"""
        if provider != "google":
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Provider '{provider}' is not supported",
            )

        # Generate and cache state for CSRF protection
        state = secrets.token_urlsafe(32)
        await self.cache_client.set(
            key=f"oauth_state:{state}",
            value=state,
            expires=600,  # 10 minutes
        )

        # Build authorization URL
        params = {
            "client_id": google_oauth_settings.google_client_id,
            "redirect_uri": google_oauth_settings.google_redirect_url,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }

        auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
        return {"url": auth_url}

    async def handle_oauth_callback(
        self,
        provider: Literal["apple", "google"],
        code: str,
        state: str,
        role: Literal["careseeker", "caregiver"],
    ) -> TokenResponse:
        """Handle OAuth2 callback and create/update user"""
        if provider != "google":
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Provider '{provider}' is not supported",
            )

        # Validate state (CSRF protection)
        await self._validate_oauth_state(state)

        # Exchange code for tokens
        token_data = await self._exchange_code_for_token(code)

        # Get user info from provider
        user_info = await self._fetch_google_user_info(token_data["access_token"])

        # Create or update user and account
        user = await self._create_or_update_oauth_user(
            user_info=user_info,
            token_data=token_data,
            provider=provider,
            role=role,
        )

        # Create session and tokens
        return await self._create_user_session(user.id)

    # ===== Helper Methods =====

    async def _get_user_or_404(
        self,
        user_id: UUID | None = None,
        email: str | None = None,
        error_message: str = "User not found",
    ) -> User:
        """Get user by ID or email, raise 404 if not found"""
        if user_id:
            user = await self.user_repository.get_user(user_id=user_id)
        elif email:
            user = await self.user_repository.get_user_by_email(email=email)
        else:
            raise ValueError("Either user_id or email must be provided")

        if not user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=error_message,
            )
        return user

    async def _get_credentials_account(self, user_id: UUID) -> Account | None:
        """Get user's credentials account if it exists"""
        accounts = await self.account_repository.get_accounts_by_user_id(
            user_id=user_id
        )
        return next((acc for acc in accounts if acc.provider_id == "credentials"), None)

    async def _get_credentials_account_or_401(self, user_id: UUID) -> Account:
        """Get credentials account or raise 401"""
        account = await self._get_credentials_account(user_id)
        if not account or not account.password:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        return account

    async def _get_credentials_account_or_404(self, user_id: UUID) -> Account:
        """Get credentials account or raise 404"""
        account = await self._get_credentials_account(user_id)
        if not account:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="No credentials account found",
            )
        return account

    async def _get_session_or_404(self, session_id: UUID):
        """Get session or raise 404"""
        session = await self.session_repository.get_session_by_id(session_id=session_id)
        if not session:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Session not found",
            )
        return session

    async def _get_verification_code_or_404(
        self,
        token: str,
        expected_type: VerificationCodeEnum,
    ):
        """Get verification code by token and validate type"""
        code = await self.verification_code_repository.get_verification_code_by_token(
            token=token
        )

        if not code:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Verification code is invalid or expired",
            )

        if code.identifier != expected_type:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid verification code type",
            )

        return code

    def _check_verification_code_expiry(self, verification_code) -> None:
        """Check if verification code has expired"""
        if verification_code.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Verification code has expired",
            )

    def _verify_password(self, stored_hash: str, provided_password: str) -> None:
        """Verify password matches hash, raise 401 if not"""
        try:
            self.password_hasher.verify(stored_hash, provided_password)
        except VerifyMismatchError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

    async def _assign_roles_to_user(
        self, user_id: UUID, role_names: list[RoleEnum]
    ) -> None:
        """Assign roles to user"""
        for role_name in role_names:
            role = await self.role_repository.get_role_by_name(name=role_name.value)
            if role:
                await self.user_to_role_repository.create_user_to_role(
                    user_id=user_id,
                    role_id=role.id,
                )
                self.logger.info(f"Assigned role {role_name} to user {user_id}")

    async def _send_verification_email(self, user: User) -> None:
        """Generate verification code and send email"""
        code = self._generate_verification_code()
        token = secrets.token_urlsafe(32)

        await self.verification_code_repository.create_verification_code(
            CreateVerificationCodeSchema(
                value=code,
                token=token,
                user_id=user.id,
                expires_at=datetime.now(timezone.utc)
                + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES),
                identifier=VerificationCodeEnum.VERIFY_EMAIL,
            )
        )

        verification_url = f"{base_settings.base_url}/verify-email?token={token}"
        self.email_client.send_verification_email(
            email=user.email,
            code=code,
            link=verification_url,
        )

    async def _create_user_session(self, user_id: UUID) -> TokenResponse:
        """Create session and generate tokens for user"""
        # Get user roles
        roles = await self.role_repository.get_roles_by_user_id(user_id=user_id)

        # Create session
        session = await self.session_repository.create_session(
            CreateSessionSchema(
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=SESSION_EXPIRE_DAYS),
                user_id=user_id,
            )
        )

        # Generate tokens
        access_token = self.jwt_client.create_access_token(
            user_id=user_id,
            session_id=session.id,
            roles=[role.name for role in roles],
        )
        refresh_token = self.jwt_client.create_refresh_token(
            user_id=user_id,
            session_id=session.id,
        )

        return TokenResponse.model_validate(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

    def _generate_verification_code(self) -> str:
        """Generate 6-digit verification code"""
        return str(random.randint(100000, 999999))

    # ===== OAuth Helper Methods =====

    async def _validate_oauth_state(self, state: str) -> None:
        """Validate OAuth state parameter"""
        cached_state = await self.cache_client.get(f"oauth_state:{state}")
        if not cached_state:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid or expired state parameter",
            )
        await self.cache_client.delete(f"oauth_state:{state}")

    async def _exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        token_request_data = {
            "code": code,
            "client_id": google_oauth_settings.google_client_id,
            "client_secret": google_oauth_settings.google_client_secret,
            "redirect_uri": google_oauth_settings.google_redirect_url,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data=token_request_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Token exchange failed: {e.response.text}")
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Failed to authenticate with provider",
                )
            except httpx.RequestError as e:
                self.logger.error(f"Provider connection failed: {str(e)}")
                raise HTTPException(
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    detail="Failed to connect to authentication provider",
                )

    async def _fetch_google_user_info(self, access_token: str) -> dict:
        """Fetch user information from Google"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                self.logger.error(f"User info fetch failed: {e.response.text}")
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Failed to fetch user information",
                )
            except httpx.RequestError as e:
                self.logger.error(f"Provider connection failed: {str(e)}")
                raise HTTPException(
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    detail="Failed to connect to authentication provider",
                )

    async def _create_or_update_oauth_user(
        self,
        user_info: dict,
        token_data: dict,
        provider: Literal["google"],
        role: Literal["careseeker", "caregiver"],
    ) -> User:
        """Create new user or update existing user with OAuth info"""
        provider_user_id = user_info["id"]
        email = user_info["email"]

        # Check if OAuth account exists
        account = (
            await self.account_repository.get_account_by_account_id_and_provider_id(
                provider_id=provider,
                account_id=provider_user_id,
            )
        )

        if account:
            # Update existing OAuth account
            await self._update_oauth_account(account, user_info, token_data)
            user = await self._get_user_or_404(user_id=account.user_id)
            self.logger.info(f"Updated OAuth account for user {user.id}")
            return user

        # Check if user exists with this email
        existing_user = await self.user_repository.get_user_by_email(email=email)

        if existing_user:
            # Link OAuth to existing user
            await self._link_oauth_to_existing_user(
                user=existing_user,
                provider=provider,
                provider_user_id=provider_user_id,
                user_info=user_info,
                token_data=token_data,
            )
            self.logger.info(f"Linked OAuth to existing user {existing_user.id}")
            return existing_user

        # Create new user with OAuth
        user = await self._create_new_oauth_user(
            email=email,
            provider=provider,
            provider_user_id=provider_user_id,
            user_info=user_info,
            token_data=token_data,
            role=role,
        )
        self.logger.info(f"Created new OAuth user {user.id}")
        return user

    async def _update_oauth_account(
        self,
        account: Account,
        user_info: dict,
        token_data: dict,
    ) -> None:
        """Update existing OAuth account with new tokens"""
        await self.account_repository.update_account(
            account_id=account.id,
            provider_id=account.provider_id,
            values=UpdateAccountSchema(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                id_token=token_data.get("id_token"),
                access_token_expires_at=token_data.get("expires_in"),
            ),
        )

        # Update user profile if needed
        await self.user_repository.update_user(
            user_id=account.user_id,
            values=UpdateUserSchema.model_validate(
                {
                    "first_name": user_info.get("given_name"),
                    "last_name": user_info.get("family_name"),
                }
            ),
        )

    async def _link_oauth_to_existing_user(
        self,
        user: User,
        provider: str,
        provider_user_id: str,
        user_info: dict,
        token_data: dict,
    ) -> None:
        """Link OAuth account to existing email/password user"""
        # Create OAuth account
        await self.account_repository.create_account(
            CreateAccountSchema(
                account_id=provider_user_id,
                provider_id=provider,
                user_id=user.id,
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                id_token=token_data.get("id_token"),
                access_token_expires_at=token_data.get("expires_in"),
            )
        )

        # Mark email as verified (provider verified it)
        await self.user_repository.update_user(
            user_id=user.id,
            values=UpdateUserSchema.model_validate({"email_verified": True}),
        )

    async def _create_new_oauth_user(
        self,
        email: str,
        provider: str,
        provider_user_id: str,
        user_info: dict,
        token_data: dict,
        role: Literal["caregiver", "careseeker"],
    ) -> User:
        """Create new user from OAuth information"""
        # Create user
        user = await self.user_repository.create_user(
            values=CreateUserSchema.model_validate(
                {
                    "email": email,
                    "first_name": user_info.get("given_name", ""),
                    "last_name": user_info.get("family_name", ""),
                    "email_verified": True,
                }
            )
        )

        # Create OAuth account
        await self.account_repository.create_account(
            CreateAccountSchema(
                account_id=provider_user_id,
                provider_id=provider,
                user_id=user.id,
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                id_token=token_data.get("id_token"),
                access_token_expires_at=token_data.get("expires_in"),
            )
        )

        # Assign role
        await self._assign_roles_to_user(user.id, [RoleEnum(role)])

        return user
