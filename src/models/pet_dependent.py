import enum
import uuid

from sqlalchemy import UUID, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


# "cat", "dog", "bird", "fish", "reptile", "other"
class PetDependentSpeciesEnum(enum.Enum):
    CAT = "cat"
    DOG = "dog"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    OTHER = "other"


class PetDependent(Base):
    __tablename__ = "pet_dependent"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    dependent_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("dependent.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    species: Mapped[PetDependentSpeciesEnum] = mapped_column(
        Enum(PetDependentSpeciesEnum), nullable=False
    )
