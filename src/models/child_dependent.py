import enum
import uuid

from sqlalchemy import UUID, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ChildGenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class ChildDependent(Base):
    __tablename__ = "child_dependent"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    dependent_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("dependent.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    gender: Mapped[ChildGenderEnum | None] = mapped_column(
        Enum(ChildGenderEnum), default=None
    )  # optional

    def __repr__(self) -> str:
        return f"<ChildDependent(id={self.id}, dependent_id={self.dependent_id}, gender={self.gender})>"
