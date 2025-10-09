import enum
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AppointmentStatusEnum(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatusEnum] = mapped_column(
        Enum(AppointmentStatusEnum), nullable=False
    )
    careseeker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("careseeker_information.user_id"),
        nullable=False,
        index=True,
    )
    caregiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("caregiver_information.user_id"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, start_time={self.start_time}, end_time={self.end_time}, status={self.status}, careseeker_id={self.careseeker_id}, caregiver_id={self.caregiver_id})>"
