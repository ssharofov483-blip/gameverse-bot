from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.clan_member import ClanMember


class Clan(Base, TimestampMixin):
    __tablename__ = "clans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    tag: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    leader_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    trophies: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    treasury_gold: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    members: Mapped[List["ClanMember"]] = relationship("ClanMember", back_populates="clan", cascade="all, delete-orphan")
