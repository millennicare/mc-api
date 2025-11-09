from time import perf_counter
from uuid import UUID

from sqlalchemy import insert, select, update

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.account import Account
from src.schemas.account_schemas import CreateAccountSchema

logger = setup_logger(name=__name__)


class AccountRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_account(self, values: CreateAccountSchema) -> None:
        start = perf_counter()

        statement = insert(Account).values(**values.model_dump())
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"AccountRepository.create_account took {elapsed_ms:.2f}ms")

    async def get_accounts_by_user_id(self, user_id: UUID) -> list[Account]:
        start = perf_counter()

        statement = select(Account).where(Account.user_id == user_id)
        result = await self.db.scalars(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(
            f"AccountRepository.get_accounts_by_user_id took {elapsed_ms:.2f}ms"
        )

        return list(result.all())

    async def update_account(
        self, user_id: UUID, provider_id: str, values: dict
    ) -> None:
        start = perf_counter()

        statement = (
            update(Account)
            .where(Account.user_id == user_id and Account.provider_id == provider_id)
            .values(**values)
        )
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"AccountRepository.update_account took {elapsed_ms:.2f}ms")
