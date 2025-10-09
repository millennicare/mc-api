from typing import Annotated

from fastapi import Depends

from src.clients.email import EmailClient
from src.clients.token import JWTClient
from src.core.config import email_settings
from src.core.deps import T_Database
from src.repositories.account_repository import AccountRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.user_to_role_repository import UserToRoleRepository
from src.repositories.verification_code_repository import VerificationCodeRepository
from src.services.auth_service import AuthService


class AuthDependencies:
    def __init__(self, db: T_Database):
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.account_repository = AccountRepository(db)
        self.user_to_role_repository = UserToRoleRepository(db)
        self.verification_code_repository = VerificationCodeRepository(db)
        self.session_repository = SessionRepository(db)
        self.email_client = EmailClient(
            api_key=email_settings.resend_api_key, from_email=email_settings.from_email
        )
        self.jwt_client = JWTClient()
        self.service = AuthService(
            account_repository=self.account_repository,
            user_repository=self.user_repository,
            role_repository=self.role_repository,
            user_to_role_repository=self.user_to_role_repository,
            verification_code_repository=self.verification_code_repository,
            session_repository=self.session_repository,
            email_client=self.email_client,
            jwt_client=self.jwt_client,
        )


def get_auth_deps(db: T_Database) -> AuthDependencies:
    return AuthDependencies(db)


T_AuthDeps = Annotated[AuthDependencies, Depends(get_auth_deps)]
