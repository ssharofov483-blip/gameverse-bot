from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ItemType(str, Enum):
    WEAPON = "weapon"       # Qurol
    ARMOR = "armor"         # Sovut
    HELMET = "helmet"       # Dubulg'a
    TALISMAN = "talisman"   # Tumor / Artefakt


class ItemRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class InventoryItem(Base, TimestampMixin):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    item_type: Mapped[str] = mapped_column(String(32), nullable=False)
    rarity: Mapped[str] = mapped_column(String(32), default=ItemRarity.COMMON.value, nullable=False)

    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="inventory")

    __table_args__ = (
        Index("ix_inventory_user_equipped", "user_id", "is_equipped"),
    )
