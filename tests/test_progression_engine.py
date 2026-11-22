import pytest
from app.engine.progression import ProgressionEngine


def test_level_up_calculation():
    # Level 1 requires 500 XP
    res1 = ProgressionEngine.add_experience(current_level=1, current_xp=0, gained_xp=200)
    assert res1["level"] == 1
    assert res1["experience"] == 200
    assert res1["leveled_up"] is False

    # Gain enough to level up
    res2 = ProgressionEngine.add_experience(current_level=1, current_xp=200, gained_xp=400)
    assert res2["level"] == 2
    assert res2["experience"] == 100  # 600 - 500 = 100
    assert res2["leveled_up"] is True


def test_trophies_delta():
    # Equal players, attacker wins
    att_gain, def_loss = ProgressionEngine.calculate_trophies_delta(
        attacker_trophies=1000,
        defender_trophies=1000,
        attacker_won=True
    )
    assert att_gain > 0
    assert def_loss < 0

    # Underdog beats strong player
    underdog_gain, _ = ProgressionEngine.calculate_trophies_delta(
        attacker_trophies=800,
        defender_trophies=1200,
        attacker_won=True
    )
    assert underdog_gain > att_gain
