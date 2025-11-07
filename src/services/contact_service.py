from src.repositories.contact_repository import ContactRepository
from src.schemas.contact_schemas import ContactSchema, CreateContactSchema


class ContactService:
    def __init__(self, contact_repository: ContactRepository):
        self.contact_repository = contact_repository

    async def create_contact(self, values: CreateContactSchema) -> ContactSchema:
        return ContactSchema.model_validate(
            await self.contact_repository.create_contact(values)
        )
