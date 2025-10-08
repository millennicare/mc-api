from typing import Annotated

from fastapi import Depends

from src.core.deps import T_Database
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService


class AuthDependencies:
    def __init__(self, db: T_Database):
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.service = AuthService(
            user_repository=self.user_repository,
            role_repository=self.role_repository,
        )


def get_auth_deps(db: T_Database) -> AuthDependencies:
    return AuthDependencies(db)


T_AuthDeps = Annotated[AuthDependencies, Depends(get_auth_deps)]
