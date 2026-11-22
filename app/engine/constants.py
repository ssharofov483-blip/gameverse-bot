from typing import Dict, Any

# Building Costs and Multipliers
# Cost = base_cost * (multiplier ** (level - 1))
BUILDING_CONFIG: Dict[str, Dict[str, Any]] = {
    "town_hall": {
        "name_uz": "Qirollik Qasri 🏰",
        "base_gold": 500,
        "base_wood": 500,
        "base_iron": 300,
        "multiplier": 1.6,
        "capacity_multiplier": 5000,  # Each level adds 5,000 to max resource capacity
    },
    "gold_mine": {
        "name_uz": "Oltin Koni 🪙",
        "base_gold": 200,
        "base_wood": 300,
        "base_iron": 100,
        "multiplier": 1.45,
        "base_rate_per_hour": 150,  # level 1 = 150/hr
    },
    "lumber_mill": {
        "name_uz": "Yog‘och Kesish Joyi 🪵",
        "base_gold": 150,
        "base_wood": 200,
        "base_iron": 80,
        "multiplier": 1.45,
        "base_rate_per_hour": 180,
    },
    "iron_mine": {
        "name_uz": "Temir Koni ⛏",
        "base_gold": 250,
        "base_wood": 350,
        "base_iron": 200,
        "multiplier": 1.5,
        "base_rate_per_hour": 100,
    },
    "farm": {
        "name_uz": "Ferma 🌾",
        "base_gold": 150,
        "base_wood": 200,
        "base_iron": 50,
        "multiplier": 1.4,
        "base_rate_per_hour": 220,
    },
    "barracks": {
        "name_uz": "Kazarma 🪖",
        "base_gold": 400,
        "base_wood": 400,
        "base_iron": 300,
        "multiplier": 1.55,
        "max_troops_per_level": 100,
    },
    "wall": {
        "name_uz": "Mudofaa Devori 🧱",
        "base_gold": 300,
        "base_wood": 500,
        "base_iron": 400,
        "multiplier": 1.5,
        "defense_bonus_per_level": 50,  # Adds flat defense to kingdom in battles
    },
    "academy": {
        "name_uz": "Akademiya 🏛",
        "base_gold": 600,
        "base_wood": 600,
        "base_iron": 500,
        "multiplier": 1.6,
        "tech_bonus_per_level": 0.05,  # 5% attack/defense boost per level
    },
}

# Troop Types, Stats, and Recruitment Costs
TROOP_CONFIG: Dict[str, Dict[str, Any]] = {
    "militia": {
        "name_uz": "Oddiy Askar 🗡",
        "attack": 10,
        "defense": 8,
        "hp": 25,
        "carry_capacity": 15,
        "cost_gold": 30,
        "cost_wood": 20,
        "cost_iron": 10,
        "cost_food": 25,
        "required_barracks": 1,
    },
    "archer": {
        "name_uz": "Kamonchi 🏹",
        "attack": 22,
        "defense": 12,
        "hp": 30,
        "carry_capacity": 20,
        "cost_gold": 60,
        "cost_wood": 70,
        "cost_iron": 25,
        "cost_food": 40,
        "required_barracks": 2,
    },
    "swordsman": {
        "name_uz": "Qilichboz ⚔️",
        "attack": 28,
        "defense": 26,
        "hp": 55,
        "carry_capacity": 25,
        "cost_gold": 90,
        "cost_wood": 40,
        "cost_iron": 60,
        "cost_food": 50,
        "required_barracks": 3,
    },
    "knight": {
        "name_uz": "Ritsar (Otliq) 🐎",
        "attack": 55,
        "defense": 45,
        "hp": 110,
        "carry_capacity": 50,
        "cost_gold": 200,
        "cost_wood": 80,
        "cost_iron": 140,
        "cost_food": 120,
        "required_barracks": 5,
    },
    "catapult": {
        "name_uz": "Katapulta ☄️",
        "attack": 90,
        "defense": 20,
        "hp": 80,
        "carry_capacity": 80,
        "cost_gold": 350,
        "cost_wood": 300,
        "cost_iron": 250,
        "cost_food": 80,
        "required_barracks": 6,
    },
}

# Tactical Counter Bonuses (Attacker type vs Defender type multiplier)
COUNTER_MATRIX: Dict[str, Dict[str, float]] = {
    "archer": {"swordsman": 1.30, "militia": 1.15},       # Archers shred infantry from afar
    "swordsman": {"militia": 1.35, "knight": 0.90},       # Swordsmen slice militia
    "knight": {"archer": 1.40, "militia": 1.30},          # Knights trample archers
    "catapult": {"wall": 1.60, "swordsman": 1.10},        # Catapults crush fortifications
    "militia": {"catapult": 1.25},                         # Militia can swarm slow siege
}

# PvE Campaign Levels (NPC Enemies)
PVE_CAMPAIGNS = [
    {
        "id": 1,
        "name": "Goblinlar qarorgohi 👺",
        "description": "Yaqin o'rmondagi yovvoyi goblinlar qishloqqa hujum qilmoqda.",
        "army": {"militia": 15},
        "reward_gold": 300,
        "reward_wood": 250,
        "reward_iron": 100,
        "reward_food": 200,
        "trophies": 20,
    },
    {
        "id": 2,
        "name": "Qaroqchilar qal'asi 🏴‍☠️",
        "description": "Tog' darasidagi xavfli qaroqchilar to'dasi.",
        "army": {"militia": 30, "archer": 15},
        "reward_gold": 700,
        "reward_wood": 600,
        "reward_iron": 350,
        "reward_food": 450,
        "trophies": 35,
    },
    {
        "id": 3,
        "name": "Qora Ritsarlar istehkomi 🛡",
        "description": "Eski qirollik xoinlari tomonidan qo'riqlanadigan qasr.",
        "army": {"archer": 35, "swordsman": 40, "knight": 10},
        "reward_gold": 1600,
        "reward_wood": 1400,
        "reward_iron": 900,
        "reward_food": 1100,
        "trophies": 60,
    },
    {
        "id": 4,
        "name": "Ajdaho g'ori 🐉",
        "description": "Qadimgi olovli ajdaho va uning yovvoyi qo'riqchilari.",
        "army": {"swordsman": 80, "knight": 40, "catapult": 15},
        "reward_gold": 4000,
        "reward_wood": 3500,
        "reward_iron": 2500,
        "reward_food": 3000,
        "trophies": 120,
    },
]
