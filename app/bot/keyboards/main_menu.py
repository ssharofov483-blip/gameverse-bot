from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🏰 Mening qirolligim"),
            KeyboardButton(text="⚔️ Jang"),
        ],
        [
            KeyboardButton(text="🏗 Qurilish"),
            KeyboardButton(text="🪖 Qo‘shin"),
        ],
        [
            KeyboardButton(text="🎒 Inventar"),
            KeyboardButton(text="🤝 Klan"),
        ],
        [
            KeyboardButton(text="📜 Missiyalar"),
            KeyboardButton(text="🏆 Reyting"),
        ],
        [
            KeyboardButton(text="👤 Profil"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )
