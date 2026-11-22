import pytest
from app.models.user import User
from app.services.kingdom_service import KingdomService
from app.services.troop_service import TroopService
from app.services.battle_service import BattleService
from app.services.clan_service import ClanService
from app.services.mission_service import MissionService
from app.models.building import BuildingType


@pytest.mark.asyncio
async def test_kingdom_creation_and_upgrade(test_session):
    user = User(id=99901, first_name="Temur", username="temur_king")
    test_session.add(user)
    await test_session.commit()

    k_service = KingdomService(test_session)
    kingdom = await k_service.create_kingdom(user.id, "Amir Temur Saltanati")
    await test_session.commit()

    assert kingdom.name == "Amir Temur Saltanati"
    assert kingdom.resources.gold == 1200
    assert len(kingdom.buildings) == 8
    assert len(kingdom.troops) == 1

    # Upgrade Town Hall first so other buildings can be upgraded
    upg_th = await k_service.upgrade_building(user.id, BuildingType.TOWN_HALL.value)
    assert upg_th["new_level"] == 2

    # Upgrade Gold Mine
    upg_res = await k_service.upgrade_building(user.id, BuildingType.GOLD_MINE.value)
    await test_session.commit()

    assert upg_res["new_level"] == 2
    assert upg_res["xp_gained"] > 0
    assert kingdom.resources.gold < 1200


@pytest.mark.asyncio
async def test_troop_recruitment(test_session):
    user = User(id=99902, first_name="Bobur", username="bobur_shah")
    test_session.add(user)
    await test_session.commit()

    k_service = KingdomService(test_session)
    await k_service.create_kingdom(user.id, "Boburiylar")
    await test_session.commit()

    t_service = TroopService(test_session)
    rec_res = await t_service.recruit_troops(user.id, "militia", 10)
    await test_session.commit()

    assert rec_res["recruited_count"] == 10
    assert rec_res["total_count"] == 25  # 15 starter + 10


@pytest.mark.asyncio
async def test_pve_battle_flow(test_session):
    user = User(id=99903, first_name="Jaloliddin", username="manguberdi")
    test_session.add(user)
    await test_session.commit()

    k_service = KingdomService(test_session)
    await k_service.create_kingdom(user.id, "Xorazmshohlar")
    await test_session.commit()

    # Recruit strong army
    t_service = TroopService(test_session)
    await t_service.recruit_troops(user.id, "militia", 30)
    await test_session.commit()

    b_service = BattleService(test_session)
    # Attack Goblin camp (id=1)
    res = await b_service.fight_pve(user.id, 1)
    await test_session.commit()

    assert "is_winner" in res
    assert "attacker_casualties" in res
    assert len(res["rounds_log"]) >= 1


@pytest.mark.asyncio
async def test_clan_flow(test_session):
    user = User(id=99904, first_name="Alpomish", username="alpomish")
    test_session.add(user)
    await test_session.commit()

    k_service = KingdomService(test_session)
    k = await k_service.create_kingdom(user.id, "Qo'ng'irot")
    k.resources.gold += 1000
    await test_session.commit()

    c_service = ClanService(test_session)
    clan_res = await c_service.create_clan(
        user_id=user.id,
        name="Jasur Beklar",
        tag="BEKLAR",
        description="Bizning birlashgan ittifoq"
    )
    await test_session.commit()

    assert clan_res["name"] == "Jasur Beklar"
    assert clan_res["tag"] == "BEKLAR"

    # Donate to treasury
    don_res = await c_service.donate_to_treasury(user.id, 100)
    await test_session.commit()
    assert don_res["donated_amount"] == 100


@pytest.mark.asyncio
async def test_mission_system(test_session):
    user = User(id=99905, first_name="Farxod", username="farxod")
    test_session.add(user)
    await test_session.commit()

    k_service = KingdomService(test_session)
    await k_service.create_kingdom(user.id, "Shirak")
    await test_session.commit()

    m_service = MissionService(test_session)
    missions = await m_service.get_daily_missions(user.id)
    await test_session.commit()

    assert len(missions) >= 4
