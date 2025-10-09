import uuid

from sqlalchemy import UUID, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: uuid.uuid4()
    )
    account_id: Mapped[str] = mapped_column(String)
    provider_id: Mapped[str] = mapped_column(String)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    access_token: Mapped[str | None] = mapped_column(String)
    refresh_token: Mapped[str | None] = mapped_column(String)
    id_token: Mapped[str | None] = mapped_column(String)
    access_token_expires_at: Mapped[int | None] = mapped_column(Integer)
    refresh_token_expires_at: Mapped[int | None] = mapped_column(Integer)
    scope: Mapped[str | None] = mapped_column(String)
    password: Mapped[str | None] = mapped_column(String)

    def __repr__(self) -> str:
        return (
            f"Account("
            f"id={self.id}, "
            f"account_id={self.account_id}, "
            f"provider_id={self.provider_id}, "
            f"user_id={self.user_id}, "
            f"access_token={self.access_token is not None}, "
            f"refresh_token={self.refresh_token is not None}, "
            f"id_token={self.id_token is not None}, "
            f"access_token_expires_at={self.access_token_expires_at}, "
            f"refresh_token_expires_at={self.refresh_token_expires_at}, "
            f"scope={self.scope}, "
            f"password={self.password is not None}"
            f")"
        )
