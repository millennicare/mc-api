import enum
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SessionRoleEnum(str, enum.Enum):
    CARESEEKER = "careseeker"
    CAREGIVER = "caregiver"
    ADMIN = "admin"


class Session(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[SessionRoleEnum] = mapped_column(Enum(SessionRoleEnum), nullable=False)

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at}, role={self.role})>"
