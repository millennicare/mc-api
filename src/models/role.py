import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Role(Base):
    __tablename__ = "role"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4)
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
