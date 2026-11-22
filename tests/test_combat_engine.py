import pytest
from app.engine.combat import CombatEngine


def test_army_stats_calculation():
    army = {
        "militia": 10,  # 10 * 10 atk = 100, 10 * 8 def = 80
        "archer": 5,    # 5 * 22 atk = 110, 5 * 12 def = 60
    }
    stats = CombatEngine.calculate_army_stats(army, tech_bonus=0.10)
    # base atk = 210, with 10% bonus = 231
    assert stats["total_attack"] == 231
    assert stats["total_units"] == 15
    assert stats["total_carry"] == (10 * 15) + (5 * 20)


def test_counter_matrix():
    archers = {"archer": 20}
    swordsmen = {"swordsman": 20}
    knights = {"knight": 20}

    # Archers counter Swordsmen
    mult_arc_vs_swd = CombatEngine.calculate_counter_multiplier(archers, swordsmen)
    assert mult_arc_vs_swd > 1.20

    # Knights counter Archers
    mult_knt_vs_arc = CombatEngine.calculate_counter_multiplier(knights, archers)
    assert mult_knt_vs_arc > 1.30


def test_simulate_battle_attacker_wins():
    large_army = {"knight": 20, "swordsman": 30}
    small_goblin_camp = {"militia": 5}

    result = CombatEngine.simulate_battle(
        attacker_army=large_army,
        defender_army=small_goblin_camp,
        rng_seed=42
    )

    assert result["is_attacker_winner"] is True
    assert result["attacker_remaining"] > 0
    assert result["defender_remaining"] == 0
    assert len(result["rounds_log"]) >= 1


def test_pvp_loot_calculation():
    defender_res = {"gold": 1000, "wood": 1000, "iron": 500, "food": 800}
    carry_capacity = 500

    loot = CombatEngine.calculate_pvp_loot(defender_res, carry_capacity)
    total_looted = sum(loot.values())
    assert total_looted <= carry_capacity
    assert loot["gold"] > 0
    assert loot["wood"] > 0
