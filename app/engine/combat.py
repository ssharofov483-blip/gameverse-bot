import random
from typing import Dict, Any, List, Tuple
from app.engine.constants import TROOP_CONFIG, COUNTER_MATRIX


class CombatEngine:
    @staticmethod
    def calculate_army_stats(
        army: Dict[str, int],
        tech_bonus: float = 0.0,
        equipment_attack: int = 0,
        equipment_defense: int = 0,
    ) -> Dict[str, Any]:
        total_attack = equipment_attack
        total_defense = equipment_defense
        total_hp = 0
        total_carry = 0
        total_units = 0

        for t_type, count in army.items():
            if count <= 0:
                continue
            cfg = TROOP_CONFIG.get(t_type)
            if not cfg:
                continue

            total_units += count
            total_attack += cfg["attack"] * count
            total_defense += cfg["defense"] * count
            total_hp += cfg["hp"] * count
            total_carry += cfg["carry_capacity"] * count

        # Apply technology bonus multiplier
        total_attack = int(total_attack * (1.0 + tech_bonus))
        total_defense = int(total_defense * (1.0 + tech_bonus))

        return {
            "total_attack": total_attack,
            "total_defense": total_defense,
            "total_hp": total_hp,
            "total_carry": total_carry,
            "total_units": total_units,
        }

    @staticmethod
    def calculate_counter_multiplier(attacker_army: Dict[str, int], defender_army: Dict[str, int]) -> float:
        total_weight = 0
        weighted_mult = 0.0

        for a_type, a_count in attacker_army.items():
            if a_count <= 0 or a_type not in COUNTER_MATRIX:
                continue
            for d_type, d_count in defender_army.items():
                if d_count <= 0:
                    continue
                pair_weight = a_count * d_count
                mult = COUNTER_MATRIX[a_type].get(d_type, 1.0)
                weighted_mult += mult * pair_weight
                total_weight += pair_weight

        if total_weight == 0:
            return 1.0
        return weighted_mult / total_weight

    @classmethod
    def simulate_battle(
        cls,
        attacker_army: Dict[str, int],
        defender_army: Dict[str, int],
        attacker_tech_bonus: float = 0.0,
        defender_tech_bonus: float = 0.0,
        defender_wall_level: int = 0,
        attacker_eq_atk: int = 0,
        attacker_eq_def: int = 0,
        defender_eq_atk: int = 0,
        defender_eq_def: int = 0,
        rng_seed: int = None
    ) -> Dict[str, Any]:
        if rng_seed is not None:
            random.seed(rng_seed)

        # Clone armies so we can deduct casualties
        att_units = {k: int(v) for k, v in attacker_army.items() if v > 0}
        def_units = {k: int(v) for k, v in defender_army.items() if v > 0}

        rounds_log: List[Dict[str, Any]] = []
        max_rounds = 5

        # Wall adds flat defense and HP to defender
        wall_defense_bonus = defender_wall_level * 50
        wall_hp = defender_wall_level * 150

        for r_num in range(1, max_rounds + 1):
            att_stats = cls.calculate_army_stats(
                att_units,
                tech_bonus=attacker_tech_bonus,
                equipment_attack=attacker_eq_atk,
                equipment_defense=attacker_eq_def,
            )
            def_stats = cls.calculate_army_stats(
                def_units,
                tech_bonus=defender_tech_bonus,
                equipment_attack=defender_eq_atk,
                equipment_defense=defender_eq_def + wall_defense_bonus,
            )
            def_stats["total_hp"] += wall_hp

            if att_stats["total_units"] <= 0 or def_stats["total_units"] <= 0:
                break

            # Counter calculations
            att_counter_mult = cls.calculate_counter_multiplier(att_units, def_units)
            def_counter_mult = cls.calculate_counter_multiplier(def_units, att_units)

            # Random tactical modifiers between 0.85 and 1.15
            att_roll = round(random.uniform(0.85, 1.15), 2)
            def_roll = round(random.uniform(0.85, 1.15), 2)

            # Damage formulas
            # Raw Dmg = Attack * Counter * Roll - (Opponent Defense / 3)
            att_dmg = max(10, int((att_stats["total_attack"] * att_counter_mult * att_roll) - (def_stats["total_defense"] / 3.5)))
            def_dmg = max(10, int((def_stats["total_attack"] * def_counter_mult * def_roll) - (att_stats["total_defense"] / 3.5)))

            # Inflict damage & calculate casualties proportionally
            def_hp_before = def_stats["total_hp"]
            att_hp_before = att_stats["total_hp"]

            def_loss_ratio = min(1.0, att_dmg / max(1, def_hp_before))
            att_loss_ratio = min(1.0, def_dmg / max(1, att_hp_before))

            # Apply losses to individual troop stacks
            r_att_losses: Dict[str, int] = {}
            for t, count in list(att_units.items()):
                lost = min(count, int(round(count * att_loss_ratio)))
                if lost == 0 and att_loss_ratio > 0.05 and count > 0:
                    lost = 1  # at least 1 unit if high damage
                lost = min(count, lost)
                att_units[t] -= lost
                r_att_losses[t] = lost
                if att_units[t] <= 0:
                    del att_units[t]

            r_def_losses: Dict[str, int] = {}
            for t, count in list(def_units.items()):
                lost = min(count, int(round(count * def_loss_ratio)))
                if lost == 0 and def_loss_ratio > 0.05 and count > 0:
                    lost = 1
                lost = min(count, lost)
                def_units[t] -= lost
                r_def_losses[t] = lost
                if def_units[t] <= 0:
                    del def_units[t]

            rounds_log.append({
                "round": r_num,
                "attacker_dmg": att_dmg,
                "defender_dmg": def_dmg,
                "attacker_tactical_roll": att_roll,
                "defender_tactical_roll": def_roll,
                "attacker_counter_mult": round(att_counter_mult, 2),
                "defender_counter_mult": round(def_counter_mult, 2),
                "attacker_losses": r_att_losses,
                "defender_losses": r_def_losses,
                "attacker_remaining": sum(att_units.values()),
                "defender_remaining": sum(def_units.values()),
            })

            if not att_units or not def_units:
                break

        # Calculate total casualties
        total_att_casualties = {}
        for t, orig_count in attacker_army.items():
            rem = att_units.get(t, 0)
            lost = orig_count - rem
            if lost > 0:
                total_att_casualties[t] = lost

        total_def_casualties = {}
        for t, orig_count in defender_army.items():
            rem = def_units.get(t, 0)
            lost = orig_count - rem
            if lost > 0:
                total_def_casualties[t] = lost

        att_rem_count = sum(att_units.values())
        def_rem_count = sum(def_units.values())

        is_attacker_winner = att_rem_count > 0 and def_rem_count == 0

        # Calculate carry capacity of surviving attacker army
        surviving_carry = 0
        for t, count in att_units.items():
            cfg = TROOP_CONFIG.get(t)
            if cfg:
                surviving_carry += cfg["carry_capacity"] * count

        return {
            "is_attacker_winner": is_attacker_winner,
            "attacker_surviving": att_units,
            "defender_surviving": def_units,
            "attacker_remaining": att_rem_count,
            "defender_remaining": def_rem_count,
            "attacker_casualties": total_att_casualties,
            "defender_casualties": total_def_casualties,
            "surviving_carry_capacity": surviving_carry,
            "rounds_log": rounds_log,
        }

    @staticmethod
    def calculate_pvp_loot(
        defender_resources: Dict[str, int],
        carry_capacity: int,
        loot_rate: float = 0.35  # Up to 35% of defender's resources
    ) -> Dict[str, int]:
        max_stealable = {
            "gold": int(defender_resources.get("gold", 0) * loot_rate),
            "wood": int(defender_resources.get("wood", 0) * loot_rate),
            "iron": int(defender_resources.get("iron", 0) * loot_rate),
            "food": int(defender_resources.get("food", 0) * loot_rate),
        }

        total_desired = sum(max_stealable.values())
        if total_desired <= carry_capacity:
            return max_stealable

        # Scale down proportionally to fit in carry capacity
        ratio = carry_capacity / max(1, total_desired)
        return {
            "gold": int(max_stealable["gold"] * ratio),
            "wood": int(max_stealable["wood"] * ratio),
            "iron": int(max_stealable["iron"] * ratio),
            "food": int(max_stealable["food"] * ratio),
        }
