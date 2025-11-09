from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import insert, select

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
        statement = (
            insert(Contact)
            .values(
                **values.model_dump(),
                submitted_at=datetime.now(timezone.utc),
                status=ContactStatusEnum.PENDING,
                priority=ContactPriorityEnum.LOW,
            )
            .returning(Contact)
        )

        result = await self.db.execute(statement)
        await self.db.commit()
        return result.scalar_one()

    async def get_by_id(self, id: UUID) -> Contact | None:
        statement = select(Contact).where(Contact.id == id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_contacts(self, skip: int, limit: int) -> list[Contact]:
        statement = select(Contact).limit(limit).offset(skip)
        result = await self.db.scalars(statement)
        return list(result.all())
