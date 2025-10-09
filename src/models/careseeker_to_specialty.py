from sqlalchemy import Column, ForeignKey, Table

from src.core.database import Base

careseeker_to_specialty = Table(
    "careseeker_to_specialty",
    Base.metadata,
    Column(
        "careseeker_information_id",
        ForeignKey(
            "careseeker_information.user_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        primary_key=True,
    ),
    Column(
        "specialty_id",
        ForeignKey("specialty.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)
