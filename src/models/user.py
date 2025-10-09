import uuid

from sqlalchemy import UUID, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, email_verified={self.email_verified}, name={self.name})>"
