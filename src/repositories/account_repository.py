from sqlalchemy import insert

from src.core.deps import T_Database
from src.models.account import Account
from src.schemas.account_schemas import CreateAccountSchema


class AccountRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_account(self, values: CreateAccountSchema):
        statement = insert(Account).values(**values.model_dump())
        print(values.model_dump())
        await self.db.execute(statement)
