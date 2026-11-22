from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models.clan import Clan
from app.models.clan_member import ClanMember, ClanRole
from app.repositories.base_repo import BaseRepository


class ClanRepository(BaseRepository[Clan]):
    def __init__(self, session: AsyncSession):
        super().__init__(Clan, session)

    async def get_by_name(self, name: str) -> Optional[Clan]:
        stmt = select(Clan).where(Clan.name == name)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_tag(self, tag: str) -> Optional[Clan]:
        stmt = select(Clan).where(Clan.tag == tag)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_with_members(self, clan_id: int) -> Optional[Clan]:
        stmt = (
            select(Clan)
            .where(Clan.id == clan_id)
            .options(
                selectinload(Clan.members).selectinload(ClanMember.user)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_clan(self, user_id: int) -> Optional[tuple[Clan, ClanMember]]:
        stmt = (
            select(Clan, ClanMember)
            .join(ClanMember, Clan.id == ClanMember.clan_id)
            .where(ClanMember.user_id == user_id)
        )
        res = await self.session.execute(stmt)
        row = res.first()
        return (row[0], row[1]) if row else None

    async def get_leaderboard(self, limit: int = 10) -> List[Clan]:
        stmt = (
            select(Clan)
            .order_by(desc(Clan.trophies), desc(Clan.level))
            .limit(limit)
            .options(selectinload(Clan.members))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
