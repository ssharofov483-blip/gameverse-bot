from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import BigInteger, Integer, String, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.base import TimestampMixin


class BattleType(str, Enum):
    PVE = "pve"
    PVP = "pvp"


class Battle(Base, TimestampMixin):
    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    battle_type: Mapped[str] = mapped_column(String(16), default=BattleType.PVE.value, nullable=False, index=True)

    attacker_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    defender_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    npc_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    winner_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    is_attacker_winner: Mapped[bool] = mapped_column(default=False, nullable=False)

    attacker_casualties: Mapped[Dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    defender_casualties: Mapped[Dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)

    loot_gold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    loot_wood: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    loot_iron: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    loot_food: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trophies_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    rounds_log: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    __table_args__ = (
        Index("ix_battles_attacker_created", "attacker_id", "created_at"),
        Index("ix_battles_defender_created", "defender_id", "created_at"),
    )
