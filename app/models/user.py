from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.kingdom import Kingdom
    from app.models.clan_member import ClanMember
    from app.models.inventory import InventoryItem
    from app.models.mission import Mission
    from app.models.achievement import Achievement
    from app.models.transaction import Transaction


class User(Base, TimestampMixin):
    __tablename__ = "users"

    # Telegram user ID as primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    language_code: Mapped[str] = mapped_column(String(8), default="uz", nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    kingdom: Mapped[Optional["Kingdom"]] = relationship("Kingdom", back_populates="user", uselist=False, cascade="all, delete-orphan")
    clan_membership: Mapped[Optional["ClanMember"]] = relationship("ClanMember", back_populates="user", uselist=False, cascade="all, delete-orphan")
    inventory: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="user", cascade="all, delete-orphan")
    missions: Mapped[List["Mission"]] = relationship("Mission", back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[List["Achievement"]] = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
