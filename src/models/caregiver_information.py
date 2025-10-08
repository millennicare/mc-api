from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class CaregiverInformation(Base):
    __tablename__ = "caregiver_information"

    user_id: Mapped[str] = mapped_column(
        String(36),
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
