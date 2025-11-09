from time import perf_counter

from sqlalchemy import insert, select

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.waitlist import Waitlist
from src.schemas.waitlist_schemas import CreateWaitlistSchema

logger = setup_logger(__name__)


class WaitlistRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_waitlist(self, values: CreateWaitlistSchema) -> Waitlist:
        start = perf_counter()

        statement = insert(Waitlist).values(**values.model_dump()).returning(Waitlist)
        result = await self.db.execute(statement)
        await self.db.commit()

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"WaitlistRepository.create_waitlist took {elapsed_ms:.2f}ms")

        return result.scalar_one()

    async def get_waitlist_by_email(self, email: str) -> Waitlist | None:
        start = perf_counter()

        statement = select(Waitlist).where(Waitlist.email == email)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"WaitlistRepository.get_waitlist_by_email took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()
