from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Unique idempotency key to prevent double-spending and duplicate reward exploits
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    gold_delta: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    wood_delta: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    iron_delta: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    food_delta: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_user_cat", "user_id", "category"),
    )
