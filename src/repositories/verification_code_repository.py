from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID

from sqlalchemy import delete, insert, select

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.verification_code import VerificationCode, VerificationCodeEnum
from src.schemas.verification_code_schemas import CreateVerificationCodeSchema

logger = setup_logger(__name__)


class VerificationCodeRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_verification_code(
        self, values: CreateVerificationCodeSchema
    ) -> None:
        start = perf_counter()

        statement = insert(VerificationCode).values(**values.model_dump())
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(
            f"VerificationCodeRepository.create_verification_code took {elapsed_ms:.2f}ms"
        )

    async def get_verification_code(self, user_id: UUID) -> VerificationCode | None:
        start = perf_counter()

        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
        )
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(
            f"VerificationCodeRepository.get_verification_code took {elapsed_ms:.2f}ms"
        )

        return result.scalar_one_or_none()

    async def get_verification_code_by_value(
        self, value: str
    ) -> VerificationCode | None:
        start = perf_counter()

        statement = select(VerificationCode).where(
            VerificationCode.value == value,
            VerificationCode.expires_at > datetime.now(timezone.utc),
        )
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(
            f"VerificationCodeRepository.get_verification_code_by_value took {elapsed_ms:.2f}ms"
        )

        return result.scalar_one_or_none()

    async def delete_verification_code(
        self, user_id: UUID, identifier: VerificationCodeEnum
    ) -> None:
        start = perf_counter()

        statement = delete(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.identifier == identifier,
        )
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(
            f"VerificationCodeRepository.delete_verification_code took {elapsed_ms:.2f}ms"
        )
