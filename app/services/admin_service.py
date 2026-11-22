from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.user import User
from app.models.kingdom import Kingdom
from app.models.resource import Resource
from app.models.battle import Battle
from app.models.clan import Clan
from app.models.transaction import Transaction
from app.core.exceptions import UserNotFoundException
from app.core.security import generate_idempotency_key


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_overview(self) -> Dict[str, Any]:
        users_count = (await self.session.execute(select(func.count(User.id)))).scalar() or 0
        kingdoms_count = (await self.session.execute(select(func.count(Kingdom.id)))).scalar() or 0
        battles_count = (await self.session.execute(select(func.count(Battle.id)))).scalar() or 0
        clans_count = (await self.session.execute(select(func.count(Clan.id)))).scalar() or 0

        res_stmt = select(
            func.sum(Resource.gold),
            func.sum(Resource.wood),
            func.sum(Resource.iron),
            func.sum(Resource.food)
        )
        res_data = (await self.session.execute(res_stmt)).first()

        return {
            "total_users": users_count,
            "total_kingdoms": kingdoms_count,
            "total_battles": battles_count,
            "total_clans": clans_count,
            "total_economy": {
                "gold_in_circulation": res_data[0] or 0,
                "wood_in_circulation": res_data[1] or 0,
                "iron_in_circulation": res_data[2] or 0,
                "food_in_circulation": res_data[3] or 0,
            }
        }

    async def get_players(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        stmt = (
            select(User, Kingdom)
            .outerjoin(Kingdom, User.id == Kingdom.user_id)
            .order_by(desc(User.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        players = []
        for user, kingdom in res.all():
            players.append({
                "telegram_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "is_admin": user.is_admin,
                "is_banned": user.is_banned,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "kingdom_name": kingdom.name if kingdom else None,
                "kingdom_level": kingdom.level if kingdom else None,
                "trophies": kingdom.trophies if kingdom else None,
            })
        return players

    async def adjust_player_resources(
        self,
        user_id: int,
        gold: int = 0,
        wood: int = 0,
        iron: int = 0,
        food: int = 0,
        reason: str = "Admin adjustment"
    ) -> Dict[str, Any]:
        stmt = (
            select(Kingdom)
            .where(Kingdom.user_id == user_id)
        )
        res = await self.session.execute(stmt)
        kingdom = res.scalar_one_or_none()
        if not kingdom:
            raise UserNotFoundException("Foydalanuvchi yoki uning qirolligi topilmadi!")

        res_stmt = select(Resource).where(Resource.kingdom_id == kingdom.id)
        resource = (await self.session.execute(res_stmt)).scalar_one()

        resource.gold = max(0, resource.gold + gold)
        resource.wood = max(0, resource.wood + wood)
        resource.iron = max(0, resource.iron + iron)
        resource.food = max(0, resource.food + food)

        tx = Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key("admin_adj"),
            category="ADMIN_ADJUSTMENT",
            gold_delta=gold,
            wood_delta=wood,
            iron_delta=iron,
            food_delta=food,
            details=reason,
        )
        self.session.add(tx)
        await self.session.flush()

        return {
            "user_id": user_id,
            "new_resources": {
                "gold": resource.gold,
                "wood": resource.wood,
                "iron": resource.iron,
                "food": resource.food,
            },
            "reason": reason
        }
