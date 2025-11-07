from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException

from src.repositories.contact_repository import ContactRepository
from src.repositories.user_repository import UserRepository
from src.schemas.contact_schemas import ContactSchema, CreateContactSchema


class ContactService:
    def __init__(
        self, contact_repository: ContactRepository, user_repository: UserRepository
    ):
        self.contact_repository = contact_repository
        self.user_repository = user_repository

    async def create_contact(self, values: CreateContactSchema) -> ContactSchema:
        if values.user_id is not None:
            existing_user = await self.user_repository.get_user(user_id=values.user_id)
            if existing_user is None:
                values.user_id = None

        return ContactSchema.model_validate(
            await self.contact_repository.create_contact(values)
        )

    async def get_contact_by_id(self, contact_id: UUID) -> ContactSchema:
        contact = await self.contact_repository.get_by_id(contact_id)
        if contact is None:
            raise HTTPException(detail="Contact not found", status_code=HTTPStatus.NOT_FOUND)
        return ContactSchema.model_validate(contact)

    async def get_contacts(self, skip: int, limit: int) -> list[ContactSchema]:
        contacts = await self.contact_repository.get_contacts(skip=skip, limit=limit)
        return [ContactSchema.model_validate(contact) for contact in contacts]
