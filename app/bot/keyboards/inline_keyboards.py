from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.engine.constants import BUILDING_CONFIG, TROOP_CONFIG, PVE_CAMPAIGNS
from app.models.building import Building
from app.models.mission import Mission


def get_kingdom_actions_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🌾 Resurslarni yig'ish", callback_data="act_collect_res"),
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="act_refresh_kingdom"),
        ],
        [
            InlineKeyboardButton(text="🏗 Qurilishga o'tish", callback_data="nav_buildings"),
            InlineKeyboardButton(text="🪖 Kazarmaga o'tish", callback_data="nav_troops"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_buildings_keyboard(buildings: List[Building]) -> InlineKeyboardMarkup:
    buttons = []
    for b in buildings:
        cfg = BUILDING_CONFIG.get(b.building_type, {})
        name = cfg.get("name_uz", b.building_type)
        buttons.append([
            InlineKeyboardButton(
                text=f"{name} (Lv.{b.level}) ⬆️",
                callback_data=f"upg_b_{b.building_type}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Qirollikka qaytish", callback_data="act_refresh_kingdom")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_troops_recruit_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for t_type, cfg in TROOP_CONFIG.items():
        name = cfg.get("name_uz", t_type)
        buttons.append([
            InlineKeyboardButton(text=f"{name} +10", callback_data=f"rec_{t_type}_10"),
            InlineKeyboardButton(text="+50", callback_data=f"rec_{t_type}_50"),
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Qirollikka qaytish", callback_data="act_refresh_kingdom")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_battle_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="👹 PvE Kampaniyalar", callback_data="battle_pve_list"),
            InlineKeyboardButton(text="⚔️ PvP Arena", callback_data="battle_pvp_list"),
        ],
        [
            InlineKeyboardButton(text="📜 Janglar tarixi", callback_data="battle_history"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_pve_campaigns_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for c in PVE_CAMPAIGNS:
        buttons.append([
            InlineKeyboardButton(
                text=f"{c['name']} (Mukofot: {c['reward_gold']} 🪙)",
                callback_data=f"pve_fight_{c['id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Jang menyusiga qaytish", callback_data="nav_battle")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_missions_keyboard(missions: List[Mission]) -> InlineKeyboardMarkup:
    buttons = []
    for m in missions:
        if m.is_completed and not m.is_claimed:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🎁 Olish: {m.title} (+{m.reward_gold}🪙)",
                    callback_data=f"claim_m_{m.id}"
                )
            ])
    buttons.append([
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="nav_missions")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_clan_actions_keyboard(has_clan: bool) -> InlineKeyboardMarkup:
    if has_clan:
        buttons = [
            [
                InlineKeyboardButton(text="💰 Xazinaga xayriya qilish (500🪙)", callback_data="clan_donate_500"),
            ],
            [
                InlineKeyboardButton(text="👥 A'zolar ro'yxati", callback_data="clan_members"),
                InlineKeyboardButton(text="🚪 Klanni tark etish", callback_data="clan_leave"),
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="➕ Yangi klan tuzish (1,000🪙)", callback_data="clan_create_prompt"),
            ],
            [
                InlineKeyboardButton(text="🔍 Klanlar ro'yxati", callback_data="clan_list"),
            ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_leaderboard_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="👑 Qirolliklar reytingi", callback_data="lb_kingdoms"),
            InlineKeyboardButton(text="🤝 Klanlar reytingi", callback_data="lb_clans"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
