from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from app.engine.constants import BUILDING_CONFIG, TROOP_CONFIG
from app.models.building import Building, BuildingType
from app.models.resource import Resource
from app.core.exceptions import InsufficientResourcesException


class EconomyEngine:
    @staticmethod
    def get_building_upgrade_cost(building_type: str, current_level: int) -> Dict[str, int]:
        cfg = BUILDING_CONFIG.get(building_type)
        if not cfg:
            raise ValueError(f"Noma'lum bino turi: {building_type}")

        mult = cfg["multiplier"] ** (current_level - 1)
        return {
            "gold": int(cfg["base_gold"] * mult),
            "wood": int(cfg["base_wood"] * mult),
            "iron": int(cfg["base_iron"] * mult),
            "food": 0,
        }

    @staticmethod
    def get_max_storage_capacity(buildings: List[Building]) -> int:
        town_hall_level = 1
        for b in buildings:
            if b.building_type == BuildingType.TOWN_HALL.value:
                town_hall_level = b.level
                break

        cfg = BUILDING_CONFIG[BuildingType.TOWN_HALL.value]
        # Base 5,000 + 5,000 per level above 1
        return 5000 + (town_hall_level - 1) * cfg["capacity_multiplier"]

    @staticmethod
    def calculate_hourly_production(buildings: List[Building]) -> Dict[str, int]:
        production = {
            "gold": 50,   # Base kingdom income
            "wood": 40,
            "iron": 25,
            "food": 60,
        }

        for b in buildings:
            lvl = b.level
            if b.building_type == BuildingType.GOLD_MINE.value:
                base = BUILDING_CONFIG[BuildingType.GOLD_MINE.value]["base_rate_per_hour"]
                production["gold"] += int(base * (1.35 ** (lvl - 1)))
            elif b.building_type == BuildingType.LUMBER_MILL.value:
                base = BUILDING_CONFIG[BuildingType.LUMBER_MILL.value]["base_rate_per_hour"]
                production["wood"] += int(base * (1.35 ** (lvl - 1)))
            elif b.building_type == BuildingType.IRON_MINE.value:
                base = BUILDING_CONFIG[BuildingType.IRON_MINE.value]["base_rate_per_hour"]
                production["iron"] += int(base * (1.35 ** (lvl - 1)))
            elif b.building_type == BuildingType.FARM.value:
                base = BUILDING_CONFIG[BuildingType.FARM.value]["base_rate_per_hour"]
                production["food"] += int(base * (1.35 ** (lvl - 1)))

        return production

    @classmethod
    def calculate_pending_resources(
        cls,
        resource: Resource,
        buildings: List[Building],
        now: datetime = None
    ) -> Tuple[Dict[str, int], int]:
        if now is None:
            now = datetime.now(timezone.utc)

        # Make sure tz awareness matches
        last_dt = resource.last_collected_at
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        elapsed_seconds = max(0, int((now - last_dt).total_seconds()))
        # Cap idle accumulation to 24 hours (86,400 seconds) to prevent infinite accumulation
        elapsed_seconds = min(elapsed_seconds, 86400)

        rates_hourly = cls.calculate_hourly_production(buildings)
        hours = elapsed_seconds / 3600.0

        pending = {
            "gold": int(rates_hourly["gold"] * hours),
            "wood": int(rates_hourly["wood"] * hours),
            "iron": int(rates_hourly["iron"] * hours),
            "food": int(rates_hourly["food"] * hours),
        }
        return pending, elapsed_seconds

    @classmethod
    def collect_resources(
        cls,
        resource: Resource,
        buildings: List[Building],
        now: datetime = None
    ) -> Dict[str, int]:
        if now is None:
            now = datetime.now(timezone.utc)

        max_cap = cls.get_max_storage_capacity(buildings)
        resource.max_capacity = max_cap

        pending, _ = cls.calculate_pending_resources(resource, buildings, now)

        # Add resources up to max storage capacity
        gained = {
            "gold": max(0, min(pending["gold"], max_cap - resource.gold)),
            "wood": max(0, min(pending["wood"], max_cap - resource.wood)),
            "iron": max(0, min(pending["iron"], max_cap - resource.iron)),
            "food": max(0, min(pending["food"], max_cap - resource.food)),
        }

        resource.gold += gained["gold"]
        resource.wood += gained["wood"]
        resource.iron += gained["iron"]
        resource.food += gained["food"]
        resource.last_collected_at = now

        return gained

    @staticmethod
    def get_troop_recruitment_cost(troop_type: str, count: int) -> Dict[str, int]:
        if count <= 0:
            raise ValueError("Askar soni 0 dan katta bo'lishi kerak!")

        cfg = TROOP_CONFIG.get(troop_type)
        if not cfg:
            raise ValueError(f"Noma'lum askar turi: {troop_type}")

        return {
            "gold": cfg["cost_gold"] * count,
            "wood": cfg["cost_wood"] * count,
            "iron": cfg["cost_iron"] * count,
            "food": cfg["cost_food"] * count,
        }

    @staticmethod
    def check_and_deduct(resource: Resource, cost: Dict[str, int]) -> None:
        gold_cost = cost.get("gold", 0)
        wood_cost = cost.get("wood", 0)
        iron_cost = cost.get("iron", 0)
        food_cost = cost.get("food", 0)

        missing = []
        if resource.gold < gold_cost:
            missing.append(f"Oltin ({resource.gold}/{gold_cost})")
        if resource.wood < wood_cost:
            missing.append(f"Yog‘och ({resource.wood}/{wood_cost})")
        if resource.iron < iron_cost:
            missing.append(f"Temir ({resource.iron}/{iron_cost})")
        if resource.food < food_cost:
            missing.append(f"Oziq-ovqat ({resource.food}/{food_cost})")

        if missing:
            raise InsufficientResourcesException(
                f"Resurslar yetarli emas! Yetishmayapti: {', '.join(missing)}"
            )

        resource.gold -= gold_cost
        resource.wood -= wood_cost
        resource.iron -= iron_cost
        resource.food -= food_cost
