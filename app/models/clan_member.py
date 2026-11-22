from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.clan import Clan


class ClanRole(str, Enum):
    LEADER = "leader"
    CO_LEADER = "co_leader"
    ELDER = "elder"
    MEMBER = "member"


class ClanMember(Base, TimestampMixin):
    __tablename__ = "clan_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clan_id: Mapped[int] = mapped_column(Integer, ForeignKey("clans.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), default=ClanRole.MEMBER.value, nullable=False)
    donated_gold: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="clan_membership")
    clan: Mapped["Clan"] = relationship("Clan", back_populates="members")

    __table_args__ = (
        UniqueConstraint("clan_id", "user_id", name="uq_clan_user"),
        Index("ix_clan_members_clan_role", "clan_id", "role"),
    )
