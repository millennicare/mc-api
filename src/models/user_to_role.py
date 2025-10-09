from sqlalchemy import Column, ForeignKey, Table

from src.core.database import Base

user_to_role = Table(
    "user_to_role",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)
