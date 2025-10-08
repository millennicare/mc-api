from typing import Annotated

from fastapi import Depends

from src.core.deps import T_Database
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService


class UserDependencies:
    def __init__(self, db: T_Database):
        self.user_repository = UserRepository(db)
        self.service = UserService(user_repository=self.user_repository)


def get_user_deps(db: T_Database) -> UserDependencies:
    return UserDependencies(db)


T_UserDeps = Annotated[UserDependencies, Depends(get_user_deps)]
