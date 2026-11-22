from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models.kingdom import Kingdom
from app.models.resource import Resource
from app.models.building import Building
from app.models.troop import Troop
from app.repositories.base_repo import BaseRepository


class KingdomRepository(BaseRepository[Kingdom]):
    def __init__(self, session: AsyncSession):
        super().__init__(Kingdom, session)

    async def get_by_user_id(self, user_id: int) -> Optional[Kingdom]:
        stmt = (
            select(Kingdom)
            .where(Kingdom.user_id == user_id)
            .options(
                selectinload(Kingdom.resources),
                selectinload(Kingdom.buildings),
                selectinload(Kingdom.troops),
                selectinload(Kingdom.user)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id_with_relations(self, kingdom_id: int) -> Optional[Kingdom]:
        stmt = (
            select(Kingdom)
            .where(Kingdom.id == kingdom_id)
            .options(
                selectinload(Kingdom.resources),
                selectinload(Kingdom.buildings),
                selectinload(Kingdom.troops),
                selectinload(Kingdom.user)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_leaderboard(self, limit: int = 10) -> List[Kingdom]:
        stmt = (
            select(Kingdom)
            .order_by(desc(Kingdom.trophies), desc(Kingdom.level))
            .limit(limit)
            .options(selectinload(Kingdom.user))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def find_pvp_opponents(self, exclude_user_id: int, current_trophies: int, limit: int = 5) -> List[Kingdom]:
        # Match opponents within +/- 300 trophies or closest
        stmt = (
            select(Kingdom)
            .where(Kingdom.user_id != exclude_user_id)
            .order_by(desc(Kingdom.trophies))
            .limit(limit)
            .options(
                selectinload(Kingdom.user),
                selectinload(Kingdom.resources),
                selectinload(Kingdom.buildings),
                selectinload(Kingdom.troops)
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
