from typing import Annotated

from fastapi import Depends

from src.core.deps import T_Database
from src.repositories.waitlist_repository import WaitlistRepository
from src.services.waitlist_service import WaitlistService


class WaitlistDependencies:
    def __init__(self, db: T_Database):
        self.waitlist_repository = WaitlistRepository(db)
        self.service = WaitlistService(waitlist_repository=self.waitlist_repository)


def get_waitlist_deps(db: T_Database) -> WaitlistDependencies:
    return WaitlistDependencies(db)


T_WaitlistDeps = Annotated[WaitlistDependencies, Depends(get_waitlist_deps)]
