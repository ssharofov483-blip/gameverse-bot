from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.battle import Battle, BattleType
from app.models.building import BuildingType
from app.models.transaction import Transaction
from app.models.achievement import Achievement
from app.engine.constants import PVE_CAMPAIGNS
from app.engine.combat import CombatEngine
from app.engine.progression import ProgressionEngine
from app.core.exceptions import (
    KingdomNotFoundException,
    BattleException,
    ShieldActiveException,
)
from app.repositories.kingdom_repo import KingdomRepository
from app.repositories.battle_repo import BattleRepository
from app.repositories.mission_repo import MissionRepository
from app.core.security import generate_idempotency_key


class BattleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.kingdom_repo = KingdomRepository(session)
        self.battle_repo = BattleRepository(session)
        self.mission_repo = MissionRepository(session)

    async def fight_pve(self, user_id: int, campaign_id: int) -> Dict[str, Any]:
        campaign = next((c for c in PVE_CAMPAIGNS if c["id"] == campaign_id), None)
        if not campaign:
            raise BattleException(f"Bunday bosqich mavjud emas: {campaign_id}")

        attacker_kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not attacker_kingdom:
            raise KingdomNotFoundException()

        # Build attacker army dict
        att_army = {t.troop_type: t.count for t in attacker_kingdom.troops if t.count > 0}
        total_att_units = sum(att_army.values())
        if total_att_units <= 0:
            raise BattleException("Jangga kirish uchun qo'shiningizda askarlar bo'lishi kerak!")

        # Technology bonus from Academy
        academy = next((b for b in attacker_kingdom.buildings if b.building_type == BuildingType.ACADEMY.value), None)
        tech_bonus = (academy.level - 1) * 0.05 if academy else 0.0

        # Simulate Battle
        sim_result = CombatEngine.simulate_battle(
            attacker_army=att_army,
            defender_army=campaign["army"],
            attacker_tech_bonus=tech_bonus,
            defender_tech_bonus=0.0,
            defender_wall_level=0,
        )

        is_winner = sim_result["is_attacker_winner"]

        # Apply attacker casualties
        for t in attacker_kingdom.troops:
            lost = sim_result["attacker_casualties"].get(t.troop_type, 0)
            t.count = max(0, t.count - lost)

        loot_gold = 0
        loot_wood = 0
        loot_iron = 0
        loot_food = 0
        trophies_delta = 0

        if is_winner:
            loot_gold = campaign["reward_gold"]
            loot_wood = campaign["reward_wood"]
            loot_iron = campaign["reward_iron"]
            loot_food = campaign["reward_food"]
            trophies_delta = campaign["trophies"]

            # Add loot to attacker resources
            attacker_kingdom.resources.gold += loot_gold
            attacker_kingdom.resources.wood += loot_wood
            attacker_kingdom.resources.iron += loot_iron
            attacker_kingdom.resources.food += loot_food
            attacker_kingdom.trophies += trophies_delta

            # Record loot transaction
            tx = Transaction(
                user_id=user_id,
                idempotency_key=generate_idempotency_key("loot_pve"),
                category="PVE_BATTLE_LOOT",
                gold_delta=loot_gold,
                wood_delta=loot_wood,
                iron_delta=loot_iron,
                food_delta=loot_food,
                details=f"{campaign['name']} g'alabasi o'ljasi.",
            )
            self.session.add(tx)

            # Update daily mission
            await self.mission_repo.increment_mission_progress(user_id, "win_pve_battle", 1)

            # Check First Victory Achievement
            ach_stmt = select(Achievement).where(Achievement.user_id == user_id, Achievement.code == "FIRST_VICTORY")
            ach_res = await self.session.execute(ach_stmt)
            if not ach_res.scalar_one_or_none():
                ach = Achievement(
                    user_id=user_id,
                    code="FIRST_VICTORY",
                    title="Birinchi G'alaba 🗡",
                    description="Jang maydonida ilk dushmanni mag'lub etdingiz.",
                    reward_gold=600,
                )
                self.session.add(ach)

        # Save Battle record
        battle = Battle(
            battle_type=BattleType.PVE.value,
            attacker_id=user_id,
            npc_name=campaign["name"],
            winner_id=user_id if is_winner else None,
            is_attacker_winner=is_winner,
            attacker_casualties=sim_result["attacker_casualties"],
            defender_casualties=sim_result["defender_casualties"],
            loot_gold=loot_gold,
            loot_wood=loot_wood,
            loot_iron=loot_iron,
            loot_food=loot_food,
            trophies_delta=trophies_delta,
            rounds_log=sim_result["rounds_log"],
        )
        self.session.add(battle)

        await self.session.flush()
        return {
            "is_winner": is_winner,
            "campaign_name": campaign["name"],
            "attacker_casualties": sim_result["attacker_casualties"],
            "defender_casualties": sim_result["defender_casualties"],
            "loot": {
                "gold": loot_gold,
                "wood": loot_wood,
                "iron": loot_iron,
                "food": loot_food,
            },
            "trophies_delta": trophies_delta,
            "current_trophies": attacker_kingdom.trophies,
            "rounds_log": sim_result["rounds_log"],
        }

    async def fight_pvp(self, attacker_user_id: int, defender_user_id: int) -> Dict[str, Any]:
        if attacker_user_id == defender_user_id:
            raise BattleException("O'zingizga hujum qila olmaysiz!")

        attacker_kingdom = await self.kingdom_repo.get_by_user_id(attacker_user_id)
        defender_kingdom = await self.kingdom_repo.get_by_user_id(defender_user_id)

        if not attacker_kingdom:
            raise KingdomNotFoundException("Hujum qiluvchi qirollik topilmadi!")
        if not defender_kingdom:
            raise KingdomNotFoundException("Himoyalanuvchi qirollik topilmadi!")

        # Check shield
        now = datetime.now(timezone.utc)
        if defender_kingdom.shield_until:
            s_dt = defender_kingdom.shield_until
            if s_dt.tzinfo is None:
                s_dt = s_dt.replace(tzinfo=timezone.utc)
            if s_dt > now:
                raise ShieldActiveException(f"Raqib qalqon himoyasida! Qalqon muddati: {s_dt.strftime('%H:%M:%S')}")

        att_army = {t.troop_type: t.count for t in attacker_kingdom.troops if t.count > 0}
        def_army = {t.troop_type: t.count for t in defender_kingdom.troops if t.count > 0}

        if sum(att_army.values()) <= 0:
            raise BattleException("Hujum qilish uchun askarlaringiz bo'lishi kerak!")

        # Academy tech bonus
        att_academy = next((b for b in attacker_kingdom.buildings if b.building_type == BuildingType.ACADEMY.value), None)
        att_tech_bonus = (att_academy.level - 1) * 0.05 if att_academy else 0.0

        def_academy = next((b for b in defender_kingdom.buildings if b.building_type == BuildingType.ACADEMY.value), None)
        def_tech_bonus = (def_academy.level - 1) * 0.05 if def_academy else 0.0

        # Wall defense
        def_wall = next((b for b in defender_kingdom.buildings if b.building_type == BuildingType.WALL.value), None)
        def_wall_lvl = def_wall.level if def_wall else 0

        sim_result = CombatEngine.simulate_battle(
            attacker_army=att_army,
            defender_army=def_army,
            attacker_tech_bonus=att_tech_bonus,
            defender_tech_bonus=def_tech_bonus,
            defender_wall_level=def_wall_lvl,
        )

        is_winner = sim_result["is_attacker_winner"]

        # Apply casualties to attacker
        for t in attacker_kingdom.troops:
            lost = sim_result["attacker_casualties"].get(t.troop_type, 0)
            t.count = max(0, t.count - lost)

        # Apply casualties to defender
        for t in defender_kingdom.troops:
            lost = sim_result["defender_casualties"].get(t.troop_type, 0)
            t.count = max(0, t.count - lost)

        loot = {"gold": 0, "wood": 0, "iron": 0, "food": 0}
        att_trophies_delta, def_trophies_delta = ProgressionEngine.calculate_trophies_delta(
            attacker_kingdom.trophies,
            defender_kingdom.trophies,
            is_winner
        )

        if is_winner:
            # Calculate looted resources
            def_resources = {
                "gold": defender_kingdom.resources.gold,
                "wood": defender_kingdom.resources.wood,
                "iron": defender_kingdom.resources.iron,
                "food": defender_kingdom.resources.food,
            }
            loot = CombatEngine.calculate_pvp_loot(
                def_resources,
                sim_result["surviving_carry_capacity"]
            )

            # Deduct from defender
            defender_kingdom.resources.gold -= loot["gold"]
            defender_kingdom.resources.wood -= loot["wood"]
            defender_kingdom.resources.iron -= loot["iron"]
            defender_kingdom.resources.food -= loot["food"]

            # Add to attacker
            attacker_kingdom.resources.gold += loot["gold"]
            attacker_kingdom.resources.wood += loot["wood"]
            attacker_kingdom.resources.iron += loot["iron"]
            attacker_kingdom.resources.food += loot["food"]

            # Grant defender 12-hour peace shield after being defeated
            defender_kingdom.shield_until = now + timedelta(hours=12)

            # Record attacker loot tx
            self.session.add(Transaction(
                user_id=attacker_user_id,
                idempotency_key=generate_idempotency_key("pvp_loot_att"),
                category="PVP_BATTLE_LOOT",
                gold_delta=loot["gold"],
                wood_delta=loot["wood"],
                iron_delta=loot["iron"],
                food_delta=loot["food"],
                details=f"PvP g'alabasi ({defender_kingdom.name} ustidan).",
            ))

            # Record defender loss tx
            self.session.add(Transaction(
                user_id=defender_user_id,
                idempotency_key=generate_idempotency_key("pvp_loot_def"),
                category="PVP_DEFENSE_LOSS",
                gold_delta=-loot["gold"],
                wood_delta=-loot["wood"],
                iron_delta=-loot["iron"],
                food_delta=-loot["food"],
                details=f"PvP mag'lubiyati ({attacker_kingdom.name} hujumi).",
            ))

        attacker_kingdom.trophies = max(0, attacker_kingdom.trophies + att_trophies_delta)
        defender_kingdom.trophies = max(0, defender_kingdom.trophies + def_trophies_delta)

        # Save Battle record
        battle = Battle(
            battle_type=BattleType.PVP.value,
            attacker_id=attacker_user_id,
            defender_id=defender_user_id,
            winner_id=attacker_user_id if is_winner else defender_user_id,
            is_attacker_winner=is_winner,
            attacker_casualties=sim_result["attacker_casualties"],
            defender_casualties=sim_result["defender_casualties"],
            loot_gold=loot["gold"],
            loot_wood=loot["wood"],
            loot_iron=loot["iron"],
            loot_food=loot["food"],
            trophies_delta=att_trophies_delta,
            rounds_log=sim_result["rounds_log"],
        )
        self.session.add(battle)

        await self.session.flush()
        return {
            "is_winner": is_winner,
            "defender_name": defender_kingdom.name,
            "attacker_casualties": sim_result["attacker_casualties"],
            "defender_casualties": sim_result["defender_casualties"],
            "loot": loot,
            "trophies_delta": att_trophies_delta,
            "current_trophies": attacker_kingdom.trophies,
            "rounds_log": sim_result["rounds_log"],
        }
