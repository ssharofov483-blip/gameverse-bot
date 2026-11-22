from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.battle import Battle
from app.repositories.base_repo import BaseRepository


class BattleRepository(BaseRepository[Battle]):
    def __init__(self, session: AsyncSession):
        super().__init__(Battle, session)

    async def get_user_battle_history(self, user_id: int, limit: int = 10) -> List[Battle]:
        stmt = (
            select(Battle)
            .where((Battle.attacker_id == user_id) | (Battle.defender_id == user_id))
            .order_by(desc(Battle.created_at))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_total_battles_count(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count(Battle.id))
        res = await self.session.execute(stmt)
        return res.scalar() or 0
