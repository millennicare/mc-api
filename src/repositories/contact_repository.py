from datetime import datetime, timezone

from src.core.deps import T_Database
from src.models.contact import (
    Contact,
    ContactPriorityEnum,
    ContactStatusEnum,
)
from src.schemas.contact_schemas import CreateContactSchema


class ContactRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_contact(self, values: CreateContactSchema) -> Contact:
        contact = Contact(
            **values.model_dump(),
            submitted_at=datetime.now(timezone.utc),
            status=ContactStatusEnum.PENDING,
            priority=ContactPriorityEnum.LOW,
        )

        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
