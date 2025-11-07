import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ContactPriorityEnum(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ContactStatusEnum(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Contact(Base):
    __tablename__ = "contact"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ContactStatusEnum] = mapped_column(
        Enum(ContactStatusEnum), nullable=False, default=ContactStatusEnum.PENDING
    )
    priority: Mapped[ContactPriorityEnum] = mapped_column(
        Enum(ContactPriorityEnum), nullable=False, default=ContactPriorityEnum.LOW
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"Contact(id={self.id}, full_name={self.full_name}, email={self.email}, message={self.message}, status={self.status}, priority={self.priority}, submitted_at={self.submitted_at}, user_id={self.user_id})"
