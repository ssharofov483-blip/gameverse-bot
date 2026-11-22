from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.kingdom import Kingdom


class TroopType(str, Enum):
    MILITIA = "militia"         # Oddiy askar
    ARCHER = "archer"           # Kamonchi
    SWORDSMAN = "swordsman"     # Qilichboz
    KNIGHT = "knight"           # Ritsar (Otliq)
    CATAPULT = "catapult"       # Katapulta (Qamal quroli)


class Troop(Base, TimestampMixin):
    __tablename__ = "troops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kingdom_id: Mapped[int] = mapped_column(Integer, ForeignKey("kingdoms.id", ondelete="CASCADE"), nullable=False, index=True)
    troop_type: Mapped[str] = mapped_column(String(32), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    kingdom: Mapped["Kingdom"] = relationship("Kingdom", back_populates="troops")

    __table_args__ = (
        UniqueConstraint("kingdom_id", "troop_type", name="uq_kingdom_troop_type"),
        Index("ix_troops_kingdom_type", "kingdom_id", "troop_type"),
    )
