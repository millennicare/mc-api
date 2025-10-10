import random
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from fastapi import HTTPException

from src.clients.email import EmailClient
from src.clients.token import JWTClient
from src.models.verification_code import VerificationCodeEnum
from src.repositories.account_repository import AccountRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.user_to_role_repository import UserToRoleRepository
from src.repositories.verification_code_repository import VerificationCodeRepository
from src.schemas.account_schemas import CreateAccountSchema
from src.schemas.auth_schemas import SignInSchema, SignUpSchema, TokenResponse
from src.schemas.session_schemas import CreateSessionSchema
from src.schemas.user_schemas import CreateUserSchema
from src.schemas.verification_code_schemas import CreateVerificationCodeSchema

from argon2 import PasswordHasher


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

    async def sign_up(self, body: SignUpSchema) -> TokenResponse:
        existing_user = await self.user_repository.get_user_by_email(email=body.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A user with this email address already exists",
            )

        role = await self.role_repository.get_role_by_name(body.role.value)
        if role is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Invald role {body.role}",
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

        await self.user_to_role_repository.create_user_to_role(
            user_id=user.id, role_id=role.id
        )

        session = await self.session_repository.create_session(
            CreateSessionSchema(
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                user_id=user.id,
                role=body.role,
            )
        )
        access_token = self.jwt_client.create_access_token(
            user_id=user.id, session_id=session.id, role=body.role
        )
        refresh_token = self.jwt_client.create_refresh_token(
            user_id=user.id, session_id=session.id
        )

        code = self._generate_verification_code()
        await self.verification_code_repository.create_verification_code(
            CreateVerificationCodeSchema(
                value=code,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                user_id=user.id,
                identifier=VerificationCodeEnum.VERIFY_EMAIL,
            )
        )
        self.email_client.send_verification_email(email=body.email, code=code)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def sign_in(self, body: SignInSchema) -> TokenResponse:
        user = await self.user_repository.get_user_by_email(email=body.email)
        if user is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        role = await self.role_repository.get_role_by_name(name=body.role.value)
        if role is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Role {body.role.value} not found",
            )

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

        if not self._validate_password(account.password, body.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # next, find if the user has the role they are trying to sign in as
        user_has_role = await self.user_to_role_repository.user_has_role(
            user_id=user.id, role_id=role.id
        )
        if not user_has_role:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="User does not have role"
            )

        # then, create a session and create tokens
        session = await self.session_repository.create_session(
            CreateSessionSchema(
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                user_id=user.id,
                role=body.role.value,
            )
        )
        access_token = self.jwt_client.create_access_token(
            user_id=user.id, session_id=session.id, role=body.role
        )
        refresh_token = self.jwt_client.create_refresh_token(
            user_id=user.id, session_id=session.id
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def _generate_verification_code(self) -> str:
        return str(random.randint(100000, 999999))

    def _validate_password(self, hash: str, password: str) -> bool:
        ph = PasswordHasher()
        return ph.verify(hash, password)

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)
