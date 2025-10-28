import random
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException

from src.clients.email import EmailClient
from src.clients.token import JWTClient
from src.core.config import base_settings
from src.core.constants import SESSION_EXPIRE_DAYS, VERIFICATION_CODE_EXPIRE_MINUTES
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

    async def sign_up(self, body: SignUpSchema) -> UserSchema:
        existing_user = await self.user_repository.get_user_by_email(email=body.email)
        if existing_user:
            # the frontend should try to let the user sign in if this occurs
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A user with this email address already exists",
            )

        create_user_schema = CreateUserSchema(
            name=body.name, email=body.email, email_verified=False
        )
        user = await self.user_repository.create_user(create_user_schema)

        await self.account_repository.create_account(
            CreateAccountSchema(
                account_id="email",
                provider_id="credentials",
                password=self._hash_password(body.password),
                user_id=user.id,
            )
        )

        for role in body.roles:
            role = await self.role_repository.get_role_by_name(name=role)
            if role is not None:
                await self.user_to_role_repository.create_user_to_role(
                    user_id=user.id,
                    role_id=role.id,
                )

        return UserSchema.model_validate(user)

    async def sign_in(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repository.get_user_by_email(email=email)
        if user is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # if the user's email is not yet verified, create a verification code and send
        # however, if there is already an existing verification code for this purpose, delete and send another
        if not user.email_verified:
            code = self._generate_verification_code()
            await self.verification_code_repository.delete_verification_code(
                user_id=user.id, identifier=VerificationCodeEnum.VERIFY_EMAIL
            )
            await self.verification_code_repository.create_verification_code(
                CreateVerificationCodeSchema(
                    value=code,
                    user_id=user.id,
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
                    identifier=VerificationCodeEnum.VERIFY_EMAIL,
                )
            )
            self.email_client.send_verification_email(email=user.email, code=code)

        # find the users account with credentials
        accounts = await self.account_repository.get_accounts_by_user_id(
            user_id=user.id
        )
        account = next(
            (acc for acc in accounts if acc.provider_id == "credentials"), None
        )
        if account is None:
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
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def verify_email(self, code: str, user_id: str) -> None:
        verification_code = (
            await self.verification_code_repository.get_verification_code(
                user_id=user_id
            )
        )
        if verification_code is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Verification code is invalid or expired.",
            )

        if (
            verification_code.identifier != VerificationCodeEnum.VERIFY_EMAIL
            or verification_code.value != code
            or verification_code.expires_at < datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Verification code is invalid or expired.",
            )

        await self.verification_code_repository.delete_verification_code(
            user_id=user_id, identifier=VerificationCodeEnum.VERIFY_EMAIL
        )

        await self.user_repository.update_user(
            user_id=user_id, values={"email_verified": True}
        )

    async def sign_out(self, session_id: str) -> None:
        await self.session_repository.delete_session(session_id=session_id)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        # no need to throw since the decoding method throws
        decoded_refresh_token = self.jwt_client.decode_refresh_token(refresh_token)
        user_id = decoded_refresh_token.sub
        session_id = decoded_refresh_token.sessionId

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
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

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
        await self.verification_code_repository.create_verification_code(
            CreateVerificationCodeSchema(
                value=code,
                user_id=user.id,
                expires_at=datetime.now(timezone.utc)
                + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES),
                identifier=VerificationCodeEnum.FORGOT_PASSWORD,
            )
        )

        link = f"{base_settings.base_url}/reset-password?token={code}"
        self.email_client.send_password_reset_email(email=user.email, link=link)

    async def reset_password(self, body: ResetPasswordSchema) -> None:
        verification_code = await (
            self.verification_code_repository.get_verification_code_by_value(
                value=body.token
            )
        )
        if not verification_code:
            raise HTTPException(
                detail="Forgot password code is invalid or expired.",
                status_code=HTTPStatus.BAD_REQUEST,
            )

        account = await self.account_repository.get_account_by_user_id(
            user_id=verification_code.user_id
        )
        if not account or account.provider_id != "credentials":
            raise HTTPException(
                detail="User not found",
                status_code=HTTPStatus.NOT_FOUND,
            )

        hashed = self._hash_password(body.password)
        await self.account_repository.update_account(
            user_id=verification_code.user_id,
            values={"password": hashed},
        )

        await self.verification_code_repository.delete_verification_code(
            user_id=verification_code.user_id,
            identifier=VerificationCodeEnum.FORGOT_PASSWORD,
        )

    def _generate_verification_code(self) -> str:
        return str(random.randint(100000, 999999))

    def _validate_password(self, hash: str, password: str) -> bool:
        ph = PasswordHasher()
        return ph.verify(hash, password)

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)
