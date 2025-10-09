import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class CaregiverInformation(Base):
    __tablename__ = "caregiver_information"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )
    background_check_completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    profile_picture: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"<CaregiverInformation(user_id={self.user_id}, background_check_completed={self.background_check_completed}, onboarding_completed={self.onboarding_completed}, profile_picture={self.profile_picture})>"
