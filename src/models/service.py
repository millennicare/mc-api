import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ServiceCategoryEnum(enum.Enum):
    CHILD_CARE = "child_care"
    SENIOR_CARE = "senior_care"
    PET_CARE = "pet_care"
    HOUSEKEEPING = "housekeeping"
    TUTORING = "tutoring"
    OTHER = "other"


class ServicePricingTypeEnum(enum.Enum):
    HOURLY = "hourly"
    FIXED = "fixed"
    PER_JOB = "per_job"


class Service(Base):
    __tablename__ = "service"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float)
    category: Mapped[ServiceCategoryEnum] = mapped_column(
        Enum(ServiceCategoryEnum), nullable=False
    )
    pricing_type: Mapped[ServicePricingTypeEnum] = mapped_column(
        Enum(ServicePricingTypeEnum), nullable=False
    )
    caregiver_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "caregiver_information.user_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    specialty_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("specialty.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
