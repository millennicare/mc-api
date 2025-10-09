import enum
import uuid

from sqlalchemy import UUID, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SeniorDependentGenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class SeniorDependent(Base):
    __tablename__ = "senior_dependent"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    dependent_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("dependent.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    gender: Mapped[SeniorDependentGenderEnum] = mapped_column(
        Enum(SeniorDependentGenderEnum), nullable=False
    )
