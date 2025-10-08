import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SeniorDependentGenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class SeniorDependent(Base):
    __tablename__ = "senior_dependent"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    dependent_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dependent.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    gender: Mapped[SeniorDependentGenderEnum] = mapped_column(
        Enum(SeniorDependentGenderEnum), nullable=False
    )
