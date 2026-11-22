import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.models.user import User
from app.services.kingdom_service import KingdomService
from app.services.troop_service import TroopService
from app.services.battle_service import BattleService
from app.services.clan_service import ClanService
from app.services.mission_service import MissionService
from app.models.building import BuildingType


async def main():
    print("Testing async sqlite engine...")
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        print("1. Creating User...")
        user = User(id=111, first_name="Temur", username="temur")
        session.add(user)
        await session.commit()
        print("User created.")

        print("2. Creating Kingdom...")
        k_service = KingdomService(session)
        k = await k_service.create_kingdom(user.id, "Buyuk Turon")
        await session.commit()
        print(f"Kingdom created: {k.name}, gold: {k.resources.gold}")

        print("3. Upgrading Town Hall first...")
        upg_th = await k_service.upgrade_building(user.id, BuildingType.TOWN_HALL.value)
        await session.commit()
        print(f"Town Hall upgraded: Lv. {upg_th['new_level']}")

        print("4. Upgrading Gold Mine...")
        upg = await k_service.upgrade_building(user.id, BuildingType.GOLD_MINE.value)
        await session.commit()
        print(f"Building upgraded: Lv. {upg['new_level']}")

        print("5. Recruiting Troops...")
        t_service = TroopService(session)
        rec = await t_service.recruit_troops(user.id, "militia", 10)
        await session.commit()
        print(f"Troops recruited: {rec['total_count']}")

        print("6. PvE Battle...")
        b_service = BattleService(session)
        bat = await b_service.fight_pve(user.id, 1)
        await session.commit()
        print(f"Battle done: winner={bat['is_winner']}, loot={bat['loot']}")

        print("7. Creating Clan...")
        # Add 1000 gold so user can afford clan creation
        user_k = await k_service.kingdom_repo.get_by_user_id(user.id)
        user_k.resources.gold += 1000
        await session.commit()

        c_service = ClanService(session)
        clan = await c_service.create_clan(user.id, "Temuriylar", "TEMUR")
        await session.commit()
        print(f"Clan created: {clan['name']} [#{clan['tag']}]")

        print("8. Missions...")
        m_service = MissionService(session)
        missions = await m_service.get_daily_missions(user.id)
        await session.commit()
        print(f"Missions count: {len(missions)}")

    await engine.dispose()
    print("ALL SERVICES TESTS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(main())
