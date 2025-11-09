from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID

from sqlalchemy import insert, select

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.contact import (
    Contact,
    ContactPriorityEnum,
    ContactStatusEnum,
)
from src.schemas.contact_schemas import CreateContactSchema

logger = setup_logger(__name__)


class ContactRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_contact(self, values: CreateContactSchema) -> Contact:
        start = perf_counter()

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

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"ContactRepository.create_contact took {elapsed_ms:.2f}ms")

        return result.scalar_one()

    async def get_by_id(self, id: UUID) -> Contact | None:
        start = perf_counter()
        statement = select(Contact).where(Contact.id == id)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"AccountRepository.get_by_id took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()

    async def get_contacts(self, skip: int, limit: int) -> list[Contact]:
        start = perf_counter()

        statement = select(Contact).limit(limit).offset(skip)
        result = await self.db.scalars(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"AccountRepository.get_contacts took {elapsed_ms:.2f}ms")

        return list(result.all())
