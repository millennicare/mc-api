import enum
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class VerificationCodeEnum(enum.Enum):
    FORGOT_PASSWORD = "forgot_password"
    VERIFY_EMAIL = "verify_email"


class VerificationCode(Base):
    __tablename__ = "verification_code"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    value: Mapped[str] = mapped_column(String, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    identifier: Mapped[VerificationCodeEnum] = mapped_column(
        Enum(VerificationCodeEnum), nullable=False
    )
    token: Mapped[str] = mapped_column(String, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Verificationcode(id={self.id}, value={self.value}, expires_at={self.expires_at}, user_id={self.user_id}, identifier={self.identifier}, token={self.token})>"
