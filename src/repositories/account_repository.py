from time import perf_counter
from uuid import UUID

from sqlalchemy import insert, select, update

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.account import Account
from src.schemas.account_schemas import CreateAccountSchema, UpdateAccountSchema


class AccountRepository:
    def __init__(self, db: T_Database):
        self.db = db
        self.logger = setup_logger(name=__name__)

    async def create_account(self, values: CreateAccountSchema) -> None:
        start = perf_counter()

        statement = insert(Account).values(**values.model_dump())
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        self.logger.info(f"AccountRepository.create_account took {elapsed_ms:.2f}ms")

    async def get_accounts_by_user_id(self, user_id: UUID) -> list[Account]:
        start = perf_counter()

        statement = select(Account).where(Account.user_id == user_id)
        result = await self.db.scalars(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        self.logger.info(
            f"AccountRepository.get_accounts_by_user_id took {elapsed_ms:.2f}ms"
        )

        return list(result.all())

    async def update_account(
        self, account_id: UUID, provider_id: str, values: UpdateAccountSchema
    ) -> None:
        start = perf_counter()

        statement = (
            update(Account)
            .where(Account.id == account_id, Account.provider_id == provider_id)
            .values(**values.model_dump(exclude_unset=True))
        )
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        self.logger.info(f"AccountRepository.update_account took {elapsed_ms:.2f}ms")

    async def get_account_by_account_id_and_provider_id(
        self, account_id: str, provider_id: str
    ) -> Account | None:
        start = perf_counter()

        statement = select(Account).where(
            Account.account_id == account_id, Account.provider_id == provider_id
        )
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        self.logger.info(
            f"AccountRepository.get_account_by_account_id_and_provider_id took {elapsed_ms:.2f}ms"
        )

        return result.scalar_one_or_none()
