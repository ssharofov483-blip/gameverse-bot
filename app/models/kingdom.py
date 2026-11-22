from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resource import Resource
    from app.models.building import Building
    from app.models.troop import Troop


class Kingdom(Base, TimestampMixin):
    __tablename__ = "kingdoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trophies: Mapped[int] = mapped_column(Integer, default=1000, nullable=False, index=True)
    shield_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="kingdom")
    resources: Mapped[Optional["Resource"]] = relationship("Resource", back_populates="kingdom", uselist=False, cascade="all, delete-orphan")
    buildings: Mapped[List["Building"]] = relationship("Building", back_populates="kingdom", cascade="all, delete-orphan")
    troops: Mapped[List["Troop"]] = relationship("Troop", back_populates="kingdom", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_kingdoms_trophies_level", "trophies", "level"),
    )
