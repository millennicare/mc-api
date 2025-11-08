from uuid import UUID

from sqlalchemy import insert, select, update

from src.core.deps import T_Database
from src.models.account import Account
from src.schemas.account_schemas import CreateAccountSchema


class AccountRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_account(self, values: CreateAccountSchema):
        statement = insert(Account).values(**values.model_dump())
        await self.db.execute(statement)

    async def get_accounts_by_user_id(self, user_id: UUID) -> list[Account]:
        statement = select(Account).where(Account.user_id == user_id)
        result = await self.db.scalars(statement)
        return list(result.all())

    async def update_account(
        self, user_id: UUID, provider_id: str, values: dict
    ) -> None:
        statement = (
            update(Account)
            .where(Account.user_id == user_id and Account.provider_id == provider_id)
            .values(**values)
        )
        await self.db.execute(statement)
