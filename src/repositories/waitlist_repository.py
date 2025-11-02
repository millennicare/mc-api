from sqlalchemy import insert, select

from src.core.deps import T_Database
from src.models.waitlist import Waitlist
from src.schemas.waitlist_schemas import CreateWaitlistSchema


class WaitlistRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_waitlist(self, values: CreateWaitlistSchema) -> Waitlist:
        statement = insert(Waitlist).values(**values.model_dump()).returning()
        result = await self.db.execute(statement)
        await self.db.commit()
        return result.scalar_one()

    async def get_waitlist_by_email(self, email: str) -> Waitlist | None:
        statement = select(Waitlist).where(Waitlist.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
