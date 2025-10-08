import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class CaregiverAvailability(Base):
    __tablename__ = "caregiver_availability"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    caregiver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("caregiver_information.user_id"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"<CaregiverAvailability(id={self.id}, caregiver_id={self.caregiver_id}, start_time={self.start_time}, end_time={self.end_time})>"
