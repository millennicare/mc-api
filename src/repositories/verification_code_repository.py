from sqlalchemy import insert

from src.core.deps import T_Database
from src.models.verification_code import VerificationCode

from src.schemas.verification_code_schemas import CreateVerificationCodeSchema


class VerificationCodeRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_verification_code(
        self, values: CreateVerificationCodeSchema
    ) -> None:
        statement = insert(VerificationCode).values(**values.model_dump())
        await self.db.execute(statement)
