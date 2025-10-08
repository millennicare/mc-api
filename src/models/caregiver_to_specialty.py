from sqlalchemy import Column, ForeignKey, Table

from src.core.database import Base

caregiver_to_specialty = Table(
    "caregiver_to_specialty",
    Base.metadata,
    Column(
        "caregiver_information_id",
        ForeignKey("caregiver_information.user_id"),
        primary_key=True,
    ),
    Column("specialty_id", ForeignKey("specialty.id"), primary_key=True),
)
