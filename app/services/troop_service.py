from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.troop import Troop, TroopType
from app.models.building import BuildingType
from app.models.transaction import Transaction
from app.models.achievement import Achievement
from app.engine.constants import TROOP_CONFIG
from app.engine.economy import EconomyEngine
from app.core.exceptions import (
    KingdomNotFoundException,
    TroopRecruitException,
)
from app.repositories.kingdom_repo import KingdomRepository
from app.repositories.mission_repo import MissionRepository
from app.core.security import generate_idempotency_key


class TroopService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.kingdom_repo = KingdomRepository(session)
        self.mission_repo = MissionRepository(session)

    async def recruit_troops(self, user_id: int, troop_type: str, count: int) -> Dict[str, Any]:
        if count <= 0:
            raise TroopRecruitException("Askar soni kamida 1 bo'lishi kerak!")

        kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not kingdom or not kingdom.resources:
            raise KingdomNotFoundException()

        cfg = TROOP_CONFIG.get(troop_type)
        if not cfg:
            raise TroopRecruitException(f"Noma'lum askar turi: {troop_type}")

        # Check Barracks building and level
        barracks = next((b for b in kingdom.buildings if b.building_type == BuildingType.BARRACKS.value), None)
        if not barracks:
            raise TroopRecruitException("Avval Kazarma (Barracks) binosini quring!")

        required_lvl = cfg["required_barracks"]
        if barracks.level < required_lvl:
            raise TroopRecruitException(
                f"{cfg['name_uz']} yollash uchun Kazarma kamida {required_lvl}-bosqich bo'lishi kerak!"
            )

        # Check total army capacity
        current_army_size = sum(t.count for t in kingdom.troops)
        max_capacity = barracks.level * 100
        if current_army_size + count > max_capacity:
            raise TroopRecruitException(
                f"Kazarma sig'imi to'ldi! Hozirgi: {current_army_size}/{max_capacity}. Kazarmani ko'taring."
            )

        # Check and deduct resources
        cost = EconomyEngine.get_troop_recruitment_cost(troop_type, count)
        EconomyEngine.check_and_deduct(kingdom.resources, cost)

        # Update or create troop row
        target_troop = next((t for t in kingdom.troops if t.troop_type == troop_type), None)
        if target_troop:
            target_troop.count += count
        else:
            target_troop = Troop(
                kingdom_id=kingdom.id,
                troop_type=troop_type,
                count=count,
            )
            self.session.add(target_troop)

        # Record transaction
        tx = Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key("recruit"),
            category="TROOP_RECRUIT",
            gold_delta=-cost["gold"],
            wood_delta=-cost["wood"],
            iron_delta=-cost["iron"],
            food_delta=-cost["food"],
            details=f"{count} ta {cfg['name_uz']} yollangan.",
        )
        self.session.add(tx)

        # Update daily mission
        await self.mission_repo.increment_mission_progress(user_id, "recruit_troops", count)

        # Check Grand Army achievement
        new_total_army = current_army_size + count
        if new_total_army >= 100:
            ach_stmt = select(Achievement).where(Achievement.user_id == user_id, Achievement.code == "GRAND_ARMY")
            ach_res = await self.session.execute(ach_stmt)
            if not ach_res.scalar_one_or_none():
                ach = Achievement(
                    user_id=user_id,
                    code="GRAND_ARMY",
                    title="Buyuk Lashkarboshi 🪖",
                    description="Qo'shiningiz askarlari soni 100 tadan oshdi.",
                    reward_gold=1500,
                )
                self.session.add(ach)

        await self.session.flush()
        return {
            "troop_type": troop_type,
            "recruited_count": count,
            "total_count": target_troop.count,
            "cost_spent": cost,
            "current_army_size": new_total_army,
            "max_army_capacity": max_capacity,
        }
