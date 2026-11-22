from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.mission import Mission
from app.models.transaction import Transaction
from app.core.exceptions import (
    GameverseException,
    KingdomNotFoundException,
)
from app.repositories.mission_repo import MissionRepository
from app.repositories.kingdom_repo import KingdomRepository
from app.core.security import generate_idempotency_key


class MissionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mission_repo = MissionRepository(session)
        self.kingdom_repo = KingdomRepository(session)

    async def get_daily_missions(self, user_id: int) -> List[Mission]:
        return await self.mission_repo.get_or_generate_daily_missions(user_id)

    async def claim_mission(self, user_id: int, mission_id: int) -> Dict[str, Any]:
        stmt = select(Mission).where(Mission.id == mission_id, Mission.user_id == user_id)
        res = await self.session.execute(stmt)
        mission = res.scalar_one_or_none()

        if not mission:
            raise GameverseException("Missiya topilmadi!")

        if not mission.is_completed:
            raise GameverseException("Ushbu vazifa hali to'liq bajarilmagan!")

        if mission.is_claimed:
            raise GameverseException("Ushbu mukofot allaqachon qabul qilingan!")

        kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not kingdom or not kingdom.resources:
            raise KingdomNotFoundException()

        # Award rewards
        kingdom.resources.gold += mission.reward_gold
        kingdom.resources.wood += mission.reward_wood
        kingdom.resources.iron += mission.reward_iron

        mission.is_claimed = True

        # Transaction audit
        tx = Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key(f"claim_m_{mission.id}"),
            category="MISSION_REWARD",
            gold_delta=mission.reward_gold,
            wood_delta=mission.reward_wood,
            iron_delta=mission.reward_iron,
            details=f"'{mission.title}' vazifasi mukofoti olindi.",
        )
        self.session.add(tx)

        await self.session.flush()
        return {
            "mission_title": mission.title,
            "reward_gold": mission.reward_gold,
            "reward_wood": mission.reward_wood,
            "reward_iron": mission.reward_iron,
        }
