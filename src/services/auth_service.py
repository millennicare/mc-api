import random
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException

from src.clients.email import EmailClient
from src.clients.token import JWTClient
from src.core.config import base_settings
from src.core.constants import SESSION_EXPIRE_DAYS, VERIFICATION_CODE_EXPIRE_MINUTES
from src.core.logger import setup_logger
from src.models.verification_code import VerificationCodeEnum
from src.repositories.account_repository import AccountRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.user_to_role_repository import UserToRoleRepository
from src.repositories.verification_code_repository import VerificationCodeRepository
from src.schemas.account_schemas import CreateAccountSchema
from src.schemas.auth_schemas import ResetPasswordSchema, SignUpSchema, TokenResponse
from src.schemas.session_schemas import CreateSessionSchema
from src.schemas.user_schemas import CreateUserSchema, UserSchema
from src.schemas.verification_code_schemas import CreateVerificationCodeSchema


class AuthService:
    def __init__(
        self,
        account_repository: AccountRepository,
        role_repository: RoleRepository,
        session_repository: SessionRepository,
        user_repository: UserRepository,
        user_to_role_repository: UserToRoleRepository,
        verification_code_repository: VerificationCodeRepository,
        email_client: EmailClient,
        jwt_client: JWTClient,
    ):
        self.account_repository = account_repository
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.session_repository = session_repository
        self.user_to_role_repository = user_to_role_repository
        self.verification_code_repository = verification_code_repository
        self.email_client = email_client
        self.jwt_client = jwt_client
        self.logger = setup_logger(__name__)

    async def sign_up(self, body: SignUpSchema) -> UserSchema:
        existing_user = await self.user_repository.get_user_by_email(email=body.email)
        if existing_user:
            # the frontend should try to let the user sign in if this occurs
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A user with this email address already exists",
            )

        values = CreateUserSchema.model_validate(
            {"name": body.name, "email": body.email, "email_verified": False}
        )
        user = await self.user_repository.create_user(values=values)
        self.logger.info(f"AuthService.sign_up . Created user {body.email}")

        await self.account_repository.create_account(
            CreateAccountSchema(
                account_id="email",
                provider_id="credentials",
                password=self._hash_password(body.password),
                user_id=user.id,
            )
        )
        self.logger.info(
            f"AuthService.sign_up . Created account with 'provider_id' of 'credentials' for user {body.email}"
        )

        for role in body.roles:
            role = await self.role_repository.get_role_by_name(name=role)
            if role is not None:
                await self.user_to_role_repository.create_user_to_role(
                    user_id=user.id,
                    role_id=role.id,
                )
                self.logger.info(
                    f"AuthService.sign_up . Created user to role link with role {role.name} for user {body.email}"
                )

        code = self._generate_verification_code()
        token = self._generate_token()
        await self.verification_code_repository.create_verification_code(
            CreateVerificationCodeSchema(
                value=code,
                token=token,
                user_id=user.id,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
                identifier=VerificationCodeEnum.VERIFY_EMAIL,
            )
        )

        verification_url = f"{base_settings.base_url}/verify-email?token={token}"
        self.email_client.send_verification_email(
            email=user.email, code=code, link=verification_url
        )
        self.logger.info(
            f"AuthService.sign_up - Sending verification email to {user.email}"
        )

        return UserSchema.model_validate(user)

    async def sign_in(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repository.get_user_by_email(email=email)
        if user is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # find the users account with credentials
        accounts = await self.account_repository.get_accounts_by_user_id(
            user_id=user.id
        )
        account = next(
            (acc for acc in accounts if acc.provider_id == "credentials"), None
        )
        if account is None or account.password is None:
            # when this occurs, a user has made an account with a different provider such as google or facebook
            # they must sign in with that provider if they do not have a password setup
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        try:
            self._validate_password(account.password, password)
        except VerifyMismatchError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # get the roles that user has and add all of them to the token
        roles = await self.role_repository.get_roles_by_user_id(user_id=user.id)

        # then, create a session and create tokens
        session = await self.session_repository.create_session(
            CreateSessionSchema(
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=SESSION_EXPIRE_DAYS),
                user_id=user.id,
            )
        )
        access_token = self.jwt_client.create_access_token(
            user_id=user.id, session_id=session.id, roles=[role.name for role in roles]
        )
        refresh_token = self.jwt_client.create_refresh_token(
            user_id=user.id, session_id=session.id
        )

        self.logger.info(f"AuthService.sign_in - {email} logged in successfully")
        return TokenResponse.model_validate(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

    async def verify_email(self, token: str, code: str) -> None:
        # Query by token to find the verification code
        verification_code = (
            await self.verification_code_repository.get_verification_code_by_token(
                token=token
            )
        )

        if verification_code is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Verification code is invalid or expired",
            )

        # Verify it's the correct type, code matches, and not expired
        if verification_code.identifier != VerificationCodeEnum.VERIFY_EMAIL:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid verification code type",
            )

        if verification_code.value != code:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Verification code is incorrect",
            )

        if verification_code.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Verification code has expired",
            )

        # Mark email as verified
        await self.user_repository.update_user(
            user_id=verification_code.user_id, values={"email_verified": True}
        )

        # Delete the verification code (single-use)
        await self.verification_code_repository.delete_verification_code(
            user_id=verification_code.user_id,
            identifier=VerificationCodeEnum.VERIFY_EMAIL,
        )

        self.logger.info(
            f"AuthService.verify_email - User {str(verification_code.user_id)} email verified successfully"
        )

    async def sign_out(self, session_id: UUID) -> None:
        await self.session_repository.delete_session(session_id=session_id)
        self.logger.info(f"Deleted session for {str(session_id)}")

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        # no need to throw since the decoding method throws
        decoded_refresh_token = self.jwt_client.decode_refresh_token(refresh_token)
        user_id = UUID(decoded_refresh_token.sub)
        session_id = UUID(decoded_refresh_token.sessionId)

        session = await self.session_repository.get_session_by_id(session_id=session_id)
        if session is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Session not found",
            )

        await self.session_repository.update_session(
            session_id=session_id,
            values={
                "expires_at": datetime.now(timezone.utc)
                + timedelta(days=SESSION_EXPIRE_DAYS)
            },
        )

        roles = await self.role_repository.get_roles_by_user_id(user_id=user_id)

        access_token = self.jwt_client.create_access_token(
            user_id=user_id, session_id=session_id, roles=[role.name for role in roles]
        )
        refresh_token = self.jwt_client.create_refresh_token(
            user_id=user_id, session_id=session_id
        )

        self.logger.info(
            f"AuthService.refresh_token - Successfully refresh tokens for {str(user_id)}"
        )

        return TokenResponse.model_validate(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

    async def forgot_password(self, email: str) -> None:
        user = await self.user_repository.get_user_by_email(email=email)
        if user is None:
            # if the user is not found, the caller of this endpoint should not know
            # return as if the user was found and an email was sent
            return
        # if the user exists, get the accounts associated with the user and check if they have one with 'credentials'
        accounts = await self.account_repository.get_accounts_by_user_id(
            user_id=user.id
        )
        account = next(
            (acc for acc in accounts if acc.provider_id == "credentials"), None
        )
        if account is None:
            # if the user does not have a password setup, do not send an email
            return

        # try to delete the existing forgot password token from the db
        await self.verification_code_repository.delete_verification_code(
            user_id=user.id, identifier=VerificationCodeEnum.FORGOT_PASSWORD
        )

        code = self._generate_verification_code()
        token = self._generate_token()
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

        reset_url = f"{base_settings.base_url}/reset-password?token={token}"
        self.email_client.send_password_reset_email(email=user.email, link=reset_url)

    async def reset_password(self, body: ResetPasswordSchema) -> None:
        verification_code = await (
            self.verification_code_repository.get_verification_code_by_token(
                token=body.token
            )
        )
        if not verification_code:
            raise HTTPException(
                detail="Password reset code is invalid or expired",
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if verification_code.identifier != VerificationCodeEnum.FORGOT_PASSWORD:
            raise HTTPException(
                detail="Invalid code type",
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if verification_code.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                detail="Password reset code has expired",
                status_code=HTTPStatus.BAD_REQUEST,
            )

        accounts = await self.account_repository.get_accounts_by_user_id(
            user_id=verification_code.user_id
        )
        credentials_account = None
        for account in accounts:
            if account.provider_id == "credentials":
                credentials_account = account
        if credentials_account is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="No account found"
            )

        hashed = self._hash_password(body.password)
        await self.account_repository.update_account(
            user_id=verification_code.user_id,
            provider_id="credentials",
            values={"password": hashed},
        )

        await self.verification_code_repository.delete_verification_code(
            user_id=verification_code.user_id,
            identifier=VerificationCodeEnum.FORGOT_PASSWORD,
        )

    async def resend_verification(self, email: str) -> None:
        user = await self.user_repository.get_user_by_email(email=email)

        # Always return success to avoid revealing if email exists
        # This prevents email enumeration attacks
        if user is None:
            self.logger.info(
                f"AuthService.resend_verification - Email not found: {email}"
            )
            return

        # Don't send if already verified
        if user.email_verified:
            self.logger.info(
                f"AuthService.resend_verification - Email already verified: {email}"
            )
            return

        # Delete any existing verification codes (invalidate old ones)
        await self.verification_code_repository.delete_verification_code(
            user_id=user.id, identifier=VerificationCodeEnum.VERIFY_EMAIL
        )

        # Generate new code and token
        code = self._generate_verification_code()
        token = self._generate_token()
        await self.verification_code_repository.create_verification_code(
            values=CreateVerificationCodeSchema(
                token=token,
                value=code,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
                user_id=user.id,
                identifier=VerificationCodeEnum.VERIFY_EMAIL,
            )
        )

        verification_url = f"{base_settings.base_url}/verify-email?token={token}"
        self.email_client.send_verification_email(
            email=user.email, code=code, link=verification_url
        )

        self.logger.info(
            f"AuthService.resend_verification - Resent verification email to {email}"
        )

    def _generate_verification_code(self) -> str:
        return str(random.randint(100000, 999999))

    def _validate_password(self, hash: str, password: str) -> bool:
        ph = PasswordHasher()
        return ph.verify(hash, password)

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)
