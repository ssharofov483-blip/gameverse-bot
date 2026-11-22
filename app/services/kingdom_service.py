from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.kingdom import Kingdom
from app.models.resource import Resource
from app.models.building import Building, BuildingType
from app.models.troop import Troop, TroopType
from app.models.transaction import Transaction
from app.models.achievement import Achievement
from app.engine.economy import EconomyEngine
from app.engine.progression import ProgressionEngine
from app.core.exceptions import (
    KingdomNotFoundException,
    InsufficientResourcesException,
    BuildingPrerequisiteNotMetException,
)
from app.repositories.kingdom_repo import KingdomRepository
from app.repositories.mission_repo import MissionRepository
from app.core.security import generate_idempotency_key


class KingdomService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.kingdom_repo = KingdomRepository(session)
        self.mission_repo = MissionRepository(session)

    async def create_kingdom(self, user_id: int, kingdom_name: str) -> Kingdom:
        existing = await self.kingdom_repo.get_by_user_id(user_id)
        if existing:
            return existing

        kingdom = Kingdom(
            user_id=user_id,
            name=kingdom_name.strip() or "Yangi Qirollik",
            level=1,
            experience=0,
            trophies=1000,
        )
        self.session.add(kingdom)
        await self.session.flush()

        # Starter Resources
        resource = Resource(
            kingdom_id=kingdom.id,
            gold=1200,
            wood=1000,
            iron=600,
            food=1000,
            max_capacity=5000,
            last_collected_at=datetime.now(timezone.utc),
        )
        self.session.add(resource)

        # Starter Buildings
        initial_buildings = [
            BuildingType.TOWN_HALL,
            BuildingType.GOLD_MINE,
            BuildingType.LUMBER_MILL,
            BuildingType.IRON_MINE,
            BuildingType.FARM,
            BuildingType.BARRACKS,
            BuildingType.WALL,
            BuildingType.ACADEMY,
        ]
        for b_type in initial_buildings:
            b = Building(
                kingdom_id=kingdom.id,
                building_type=b_type.value,
                level=1,
                is_upgrading=False,
            )
            self.session.add(b)

        # Starter Army
        starter_troop = Troop(
            kingdom_id=kingdom.id,
            troop_type=TroopType.MILITIA.value,
            count=15,
        )
        self.session.add(starter_troop)

        # Founder Achievement
        ach = Achievement(
            user_id=user_id,
            code="FIRST_KINGDOM",
            title="Qirollik Asoschisi 👑",
            description="O'z qirolligingizni muvaffaqiyatli barpo etdingiz.",
            reward_gold=500,
        )
        self.session.add(ach)

        # Transaction audit
        tx = Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key("init_k"),
            category="STARTER_PACKAGE",
            gold_delta=1200,
            wood_delta=1000,
            iron_delta=600,
            food_delta=1000,
            details=f"Qirollik '{kingdom.name}' yaratildi.",
        )
        self.session.add(tx)

        await self.session.flush()
        return await self.kingdom_repo.get_by_id_with_relations(kingdom.id)

    async def collect_resources(self, user_id: int) -> Dict[str, Any]:
        kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not kingdom or not kingdom.resources:
            raise KingdomNotFoundException()

        gained = EconomyEngine.collect_resources(
            kingdom.resources,
            kingdom.buildings,
            datetime.now(timezone.utc)
        )

        total_gained = sum(gained.values())
        if total_gained > 0:
            tx = Transaction(
                user_id=user_id,
                idempotency_key=generate_idempotency_key("collect"),
                category="RESOURCE_COLLECTION",
                gold_delta=gained["gold"],
                wood_delta=gained["wood"],
                iron_delta=gained["iron"],
                food_delta=gained["food"],
                details="Resurslar yig'ib olindi.",
            )
            self.session.add(tx)
            await self.mission_repo.increment_mission_progress(user_id, "collect_resources", 1)

        await self.session.flush()
        return {
            "gained": gained,
            "current": {
                "gold": kingdom.resources.gold,
                "wood": kingdom.resources.wood,
                "iron": kingdom.resources.iron,
                "food": kingdom.resources.food,
                "max_capacity": kingdom.resources.max_capacity,
            }
        }

    async def upgrade_building(self, user_id: int, building_type: str) -> Dict[str, Any]:
        kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not kingdom or not kingdom.resources:
            raise KingdomNotFoundException()

        # Find target building
        target_b = next((b for b in kingdom.buildings if b.building_type == building_type), None)
        if not target_b:
            raise BuildingPrerequisiteNotMetException(f"Bino topilmadi: {building_type}")

        # Check town hall prerequisite (other buildings cannot exceed Town Hall level)
        town_hall = next((b for b in kingdom.buildings if b.building_type == BuildingType.TOWN_HALL.value), None)
        if town_hall and building_type != BuildingType.TOWN_HALL.value:
            if target_b.level >= town_hall.level:
                raise BuildingPrerequisiteNotMetException(
                    f"Bu binoni oshirish uchun avval Qirollik Qasrini {target_b.level + 1}-bosqichga ko'taring!"
                )

        cost = EconomyEngine.get_building_upgrade_cost(building_type, target_b.level)
        EconomyEngine.check_and_deduct(kingdom.resources, cost)

        target_b.level += 1

        # Calculate XP gained
        xp_gain = 50 * target_b.level
        xp_result = ProgressionEngine.add_experience(kingdom.level, kingdom.experience, xp_gain)
        kingdom.level = xp_result["level"]
        kingdom.experience = xp_result["experience"]

        # If Town Hall was upgraded, update max capacity
        if building_type == BuildingType.TOWN_HALL.value:
            kingdom.resources.max_capacity = EconomyEngine.get_max_storage_capacity(kingdom.buildings)

        # Record transaction
        tx = Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key("upg_bld"),
            category="BUILDING_UPGRADE",
            gold_delta=-cost["gold"],
            wood_delta=-cost["wood"],
            iron_delta=-cost["iron"],
            food_delta=0,
            details=f"{building_type} {target_b.level}-bosqichga ko'tarildi.",
        )
        self.session.add(tx)

        # Update daily mission
        await self.mission_repo.increment_mission_progress(user_id, "upgrade_building", 1)

        await self.session.flush()
        return {
            "building_type": building_type,
            "new_level": target_b.level,
            "cost_spent": cost,
            "xp_gained": xp_gain,
            "kingdom_level": kingdom.level,
            "leveled_up": xp_result["leveled_up"],
        }
