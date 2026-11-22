from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple


class ProgressionEngine:
    @staticmethod
    def calculate_required_xp(level: int) -> int:
        # Base XP = 500 * (1.5 ** (level - 1))
        return int(500 * (1.5 ** (level - 1)))

    @classmethod
    def add_experience(cls, current_level: int, current_xp: int, gained_xp: int) -> Dict[str, Any]:
        total_xp = current_xp + gained_xp
        new_level = current_level
        leveled_up = False

        while True:
            req = cls.calculate_required_xp(new_level)
            if total_xp >= req:
                total_xp -= req
                new_level += 1
                leveled_up = True
            else:
                break

        return {
            "level": new_level,
            "experience": total_xp,
            "leveled_up": leveled_up,
            "required_xp": cls.calculate_required_xp(new_level),
        }

    @staticmethod
    def calculate_trophies_delta(attacker_trophies: int, defender_trophies: int, attacker_won: bool) -> Tuple[int, int]:
        diff = defender_trophies - attacker_trophies
        base_gain = 30
        delta = max(10, min(50, int(base_gain + (diff * 0.05))))

        if attacker_won:
            return delta, -max(5, int(delta * 0.75))
        else:
            loss = max(10, min(40, int(base_gain - (diff * 0.05))))
            return -loss, int(loss * 0.8)

DEFAULT_MISSIONS = [
    {
        "mission_key": "collect_resources",
        "title": "Hosildorlik 🌾",
        "description": "Qirollik resurslarini 3 marta yig'ib oling.",
        "target_count": 3,
        "reward_gold": 250,
        "reward_wood": 200,
        "reward_iron": 100,
    },
    {
        "mission_key": "upgrade_building",
        "title": "Buyuk Me'mor 🏗",
        "description": "Istalgan 1 ta binoni yangi bosqichga ko'taring.",
        "target_count": 1,
        "reward_gold": 400,
        "reward_wood": 350,
        "reward_iron": 200,
    },
    {
        "mission_key": "recruit_troops",
        "title": "Armiya chaqiruvi 🪖",
        "description": "Kazamada 20 ta askar yollang.",
        "target_count": 20,
        "reward_gold": 300,
        "reward_wood": 250,
        "reward_iron": 150,
    },
    {
        "mission_key": "win_pve_battle",
        "title": "Dushmanlarni yengish ⚔️",
        "description": "PvE yurishlarida 1 marta g'alaba qozoning.",
        "target_count": 1,
        "reward_gold": 500,
        "reward_wood": 400,
        "reward_iron": 300,
    },
]

ACHIEVEMENT_DEFINITIONS = [
    {
        "code": "FIRST_KINGDOM",
        "title": "Qirollik Asoschisi 👑",
        "description": "O'z qirolligingizni muvaffaqiyatli barpo etdingiz.",
        "reward_gold": 500,
    },
    {
        "code": "FIRST_VICTORY",
        "title": "Birinchi G'alaba 🗡",
        "description": "Jang maydonida ilk dushmanni mag'lub etdingiz.",
        "reward_gold": 600,
    },
    {
        "code": "FORTRESS_BUILDER",
        "title": "Qal'a Himoyachisi 🧱",
        "description": "Mudofaa devorini 3-bosqichga ko'tardingiz.",
        "reward_gold": 1000,
    },
    {
        "code": "GRAND_ARMY",
        "title": "Buyuk Lashkarboshi 🪖",
        "description": "Qo'shiningiz askarlari soni 100 tadan oshdi.",
        "reward_gold": 1500,
    },
    {
        "code": "CLAN_LEADER",
        "title": "Ittifoq Sardori 🤝",
        "description": "Yangi klan tuzib, o'z ittifoqingizga asos soldingiz.",
        "reward_gold": 2000,
    },
]
