import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserGenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class UserInformation(Base):
    __tablename__ = "user_information"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    birthdate: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    gender: Mapped[UserGenderEnum] = mapped_column(Enum(UserGenderEnum), nullable=False)

    def __repr__(self) -> str:
        return f"<UserInformation(id={self.id}, user_id={self.user_id}, phone_number={self.phone_number}, birthdate={self.birthdate}, gender={self.gender})>"
