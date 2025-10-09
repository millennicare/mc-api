import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Role(Base):
    __tablename__ = "role"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
