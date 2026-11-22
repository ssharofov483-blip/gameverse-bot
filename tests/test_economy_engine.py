import pytest
from datetime import datetime, timezone, timedelta
from app.engine.economy import EconomyEngine
from app.models.building import Building, BuildingType
from app.models.resource import Resource
from app.core.exceptions import InsufficientResourcesException


def test_building_upgrade_cost():
    cost_lvl1 = EconomyEngine.get_building_upgrade_cost(BuildingType.GOLD_MINE.value, 1)
    cost_lvl2 = EconomyEngine.get_building_upgrade_cost(BuildingType.GOLD_MINE.value, 2)
    assert cost_lvl1["gold"] == 200
    assert cost_lvl2["gold"] == int(200 * 1.45)
    assert cost_lvl2["wood"] > cost_lvl1["wood"]


def test_max_storage_capacity():
    buildings = [
        Building(building_type=BuildingType.TOWN_HALL.value, level=1),
    ]
    cap1 = EconomyEngine.get_max_storage_capacity(buildings)
    assert cap1 == 5000

    buildings[0].level = 3
    cap3 = EconomyEngine.get_max_storage_capacity(buildings)
    assert cap3 == 5000 + (2 * 5000)  # 15,000


def test_resource_collection():
    buildings = [
        Building(building_type=BuildingType.TOWN_HALL.value, level=1),
        Building(building_type=BuildingType.GOLD_MINE.value, level=1),
        Building(building_type=BuildingType.LUMBER_MILL.value, level=1),
        Building(building_type=BuildingType.IRON_MINE.value, level=1),
        Building(building_type=BuildingType.FARM.value, level=1),
    ]

    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    res = Resource(
        kingdom_id=1,
        gold=100,
        wood=100,
        iron=100,
        food=100,
        max_capacity=5000,
        last_collected_at=one_hour_ago,
    )

    gained = EconomyEngine.collect_resources(res, buildings, now=now)
    assert gained["gold"] > 0
    assert gained["wood"] > 0
    assert res.gold == 100 + gained["gold"]
    assert res.last_collected_at == now


def test_check_and_deduct_resources():
    res = Resource(
        kingdom_id=1,
        gold=500,
        wood=500,
        iron=300,
        food=400,
        max_capacity=5000,
    )

    # Valid deduction
    EconomyEngine.check_and_deduct(res, {"gold": 200, "wood": 100, "iron": 50, "food": 50})
    assert res.gold == 300
    assert res.wood == 400
    assert res.iron == 250
    assert res.food == 350

    # Overdraft attempt
    with pytest.raises(InsufficientResourcesException):
        EconomyEngine.check_and_deduct(res, {"gold": 1000})
