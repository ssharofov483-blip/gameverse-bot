from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.kingdom import Kingdom


class Resource(Base, TimestampMixin):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kingdom_id: Mapped[int] = mapped_column(Integer, ForeignKey("kingdoms.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    gold: Mapped[int] = mapped_column(BigInteger, default=1000, nullable=False)
    wood: Mapped[int] = mapped_column(BigInteger, default=1000, nullable=False)
    iron: Mapped[int] = mapped_column(BigInteger, default=500, nullable=False)
    food: Mapped[int] = mapped_column(BigInteger, default=1000, nullable=False)

    max_capacity: Mapped[int] = mapped_column(BigInteger, default=5000, nullable=False)
    last_collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    kingdom: Mapped["Kingdom"] = relationship("Kingdom", back_populates="resources")
