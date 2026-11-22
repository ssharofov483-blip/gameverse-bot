from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from app.core.database import async_session_factory
from app.repositories.user_repo import UserRepository
from app.services.kingdom_service import KingdomService
from app.bot.keyboards.main_menu import get_main_menu_keyboard
from app.bot.keyboards.inline_keyboards import get_kingdom_actions_keyboard

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Hukmdor"
    username = message.from_user.username

    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user, is_new = await user_repo.get_or_create(
            telegram_id=user_id,
            first_name=first_name,
            username=username,
            language_code=message.from_user.language_code or "uz"
        )

        kingdom_service = KingdomService(session)
        kingdom_name = f"{first_name} Qirolligi"
        kingdom = await kingdom_service.create_kingdom(user_id, kingdom_name)
        await session.commit()

    if is_new:
        welcome_text = (
            f"👑 <b>Xush kelibsiz, buyuk Hukmdor {first_name}!</b>\n\n"
            f"Siz <b>GAMEVERSE</b> — O'rta asrlar multiplayer strategiya olamiga qadam qo'ydingiz!\n\n"
            f"🏰 <b>Qirolligingiz barpo etildi:</b> <i>{kingdom.name}</i>\n"
            f"🎁 <b>Boshlang'ich in'omlar:</b>\n"
            f"• 🪙 1,200 Oltin\n"
            f"• 🪵 1,000 Yog'och\n"
            f"• ⛏ 600 Temir\n"
            f"• 🌾 1,000 Oziq-ovqat\n"
            f"• 🗡 15 ta Oddiy Askar\n\n"
            f"Quyidagi bosh menyu orqali saltanatingizni boshqaring va dushmanlarga qarshi kurashing!"
        )
    else:
        welcome_text = (
            f"🏰 <b>Qaytganingiz bilan, Hukmdor {first_name}!</b>\n\n"
            f"Qirolligingiz: <b>{kingdom.name}</b> (Lv. {kingdom.level})\n"
            f"🏆 Kuboklar: <b>{kingdom.trophies}</b>\n\n"
            f"Saltanatingizdagi resurslarni yig'ib oling va qo'shiningizni kuchaytiring!"
        )

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
