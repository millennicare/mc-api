import enum
import uuid

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SpecialtyCategoryEnum(enum.Enum):
    CHILD_CARE = "child_care"
    SENIOR_CARE = "senior_care"
    PET_CARE = "pet_care"
    HOUSEKEEPING = "housekeeping"
    TUTORING = "tutoring"
    OTHER = "other"


class Specialty(Base):
    __tablename__ = "specialty"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    description: Mapped[str] = mapped_column(String)
    category: Mapped[SpecialtyCategoryEnum] = mapped_column(
        Enum(SpecialtyCategoryEnum), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<Specialty(id={self.id}, category={self.category}, description={self.description})>"
