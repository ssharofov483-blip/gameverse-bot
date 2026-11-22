from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Mission(Base, TimestampMixin):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    mission_key: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)

    target_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    reward_gold: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    reward_wood: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    reward_iron: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="missions")

    __table_args__ = (
        UniqueConstraint("user_id", "mission_key", name="uq_user_mission"),
        Index("ix_missions_user_claimed", "user_id", "is_claimed"),
    )
