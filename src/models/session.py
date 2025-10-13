import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Session(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
