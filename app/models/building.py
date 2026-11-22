from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.kingdom import Kingdom


class BuildingType(str, Enum):
    TOWN_HALL = "town_hall"       # Qirollik Qasri
    GOLD_MINE = "gold_mine"       # Oltin Koni
    LUMBER_MILL = "lumber_mill"   # Yog‘och Kesish Joyi
    IRON_MINE = "iron_mine"       # Temir Koni
    FARM = "farm"                 # Ferma
    BARRACKS = "barracks"         # Kazarma (Qo'shin tayyorlash)
    WALL = "wall"                 # Mudofaa Devori
    ACADEMY = "academy"           # Akademiya (Tadqiqot va texnologiya)


class Building(Base, TimestampMixin):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kingdom_id: Mapped[int] = mapped_column(Integer, ForeignKey("kingdoms.id", ondelete="CASCADE"), nullable=False, index=True)
    building_type: Mapped[str] = mapped_column(String(32), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_upgrading: Mapped[bool] = mapped_column(default=False, nullable=False)
    upgrade_finish_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    kingdom: Mapped["Kingdom"] = relationship("Kingdom", back_populates="buildings")

    __table_args__ = (
        UniqueConstraint("kingdom_id", "building_type", name="uq_kingdom_building_type"),
        Index("ix_buildings_kingdom_type", "kingdom_id", "building_type"),
    )
