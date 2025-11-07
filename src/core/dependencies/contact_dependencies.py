from typing import Annotated

from fastapi import Depends

from src.core.deps import T_Database
from src.repositories.contact_repository import ContactRepository
from src.repositories.user_repository import UserRepository
from src.services.contact_service import ContactService


class ContactDependencies:
    def __init__(self, db: T_Database):
        self.contact_repository = ContactRepository(db)
        self.user_repository = UserRepository(db)
        self.service = ContactService(
            contact_repository=self.contact_repository,
            user_repository=self.user_repository,
        )


def get_contact_deps(db: T_Database) -> ContactDependencies:
    return ContactDependencies(db)


T_ContactDeps = Annotated[ContactDependencies, Depends(get_contact_deps)]
