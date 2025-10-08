import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class DependentTypeEnum(enum.Enum):
    PET = "pet"
    CHILD = "child"
    SENIOR = "senior"


class Dependent(Base):
    __tablename__ = "dependent"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[DependentTypeEnum] = mapped_column(
        Enum(DependentTypeEnum), nullable=False
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    careseeker_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "careseeker_information.user_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
    )
