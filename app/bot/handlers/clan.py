from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.database import async_session_factory
from app.repositories.clan_repo import ClanRepository
from app.services.clan_service import ClanService
from app.bot.keyboards.inline_keyboards import get_clan_actions_keyboard

clan_router = Router()


@clan_router.message(F.text == "🤝 Klan")
@clan_router.callback_query(F.data == "nav_clan")
async def view_clan_hub(event: Message | CallbackQuery):
    user_id = event.from_user.id
    async with async_session_factory() as session:
        repo = ClanRepository(session)
        membership = await repo.get_user_clan(user_id)

    if membership:
        clan, member = membership
        text = (
            f"🤝 <b>KLAN: {clan.name} [#{clan.tag}]</b>\n"
            f"Daraja: <b>Lv. {clan.level}</b> | 🏆 Kuboklar: <b>{clan.trophies}</b>\n"
            f"Mening rolim: <b>{member.role.upper()}</b>\n"
            f"Xazinaga hissam: <b>{member.donated_gold:,} 🪙</b>\n"
            f"────────────────────\n"
            f"💰 <b>Klan xazinasi:</b> {clan.treasury_gold:,} Oltin\n"
            f"📜 <i>{clan.description or 'Tavsif mavjud emas.'}</i>"
        )
        kb = get_clan_actions_keyboard(has_clan=True)
    else:
        text = (
            "🤝 <b>KLANLAR VA ITTIFOQLAR</b>\n\n"
            "Siz hozircha hech qaysi klan a'zosi emassiz.\n\n"
            "Klan tuzish yoki unga a'zo bo'lish orqali umumiy xazinani to'ldirishingiz, "
            "klanlar urushlarida qatnashishingiz va reytingda yuqoriga ko'tarilishingiz mumkin!"
        )
        kb = get_clan_actions_keyboard(has_clan=False)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await event.answer()


@clan_router.callback_query(F.data == "clan_donate_500")
async def cb_clan_donate(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session_factory() as session:
        service = ClanService(session)
        try:
            res = await service.donate_to_treasury(user_id, 500)
            await session.commit()
            await callback.answer(f"Xazinaga 500 oltin o'tkazildi! Jami xazina: {res['clan_treasury']} 🪙", show_alert=True)
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

    await view_clan_hub(callback)


@clan_router.callback_query(F.data == "clan_list")
async def cb_clan_list(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = ClanRepository(session)
        clans = await repo.get_leaderboard(limit=5)

    if not clans:
        text = "🔍 <b>Klanlar ro'yxati hozircha bo'sh.</b> Birinchi bo'lib klan tuzing!"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="nav_clan")]
        ])
    else:
        lines = ["🔍 <b>ENG FAOL KLANLAR:</b>\n"]
        for c in clans:
            lines.append(f"• <b>{c.name}</b> [#{c.tag}] — Lv. {c.level} | 🏆 {c.trophies} kubok")
        text = "\n".join(lines)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="nav_clan")]
        ])

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()
