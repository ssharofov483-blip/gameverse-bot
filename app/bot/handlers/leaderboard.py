from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.core.database import async_session_factory
from app.repositories.kingdom_repo import KingdomRepository
from app.repositories.clan_repo import ClanRepository
from app.bot.keyboards.inline_keyboards import get_leaderboard_keyboard

leaderboard_router = Router()


@leaderboard_router.message(F.text == "🏆 Reyting")
@leaderboard_router.callback_query(F.data == "lb_kingdoms")
async def view_leaderboard(event: Message | CallbackQuery):
    async with async_session_factory() as session:
        k_repo = KingdomRepository(session)
        top_kingdoms = await k_repo.get_leaderboard(limit=10)

    lines = [
        "🏆 <b>GLOBAL QIROLLIKLAR REYTINGI (TOP-10)</b>\n",
        "Dunyoning eng qudratli hukmdorlari ro'yxati:\n"
    ]
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for idx, k in enumerate(top_kingdoms):
        medal = medals[idx] if idx < len(medals) else f"#{idx+1}"
        owner_name = k.user.first_name if k.user else "Noma'lum"
        lines.append(
            f"{medal} <b>{k.name}</b> (Lv. {k.level})\n"
            f"   Hukmdor: {owner_name} | 🏆 <b>{k.trophies}</b> kubok"
        )

    if not top_kingdoms:
        lines.append("<i>Hozircha o'yinchilar yo'q. Birinchi bo'lib yetakchilikni oling!</i>")

    text = "\n".join(lines)
    kb = get_leaderboard_keyboard()

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await event.answer()


@leaderboard_router.callback_query(F.data == "lb_clans")
async def view_clans_leaderboard(callback: CallbackQuery):
    async with async_session_factory() as session:
        clan_repo = ClanRepository(session)
        top_clans = await clan_repo.get_leaderboard(limit=10)

    lines = [
        "🏆 <b>GLOBAL KLANLAR REYTINGI (TOP-10)</b>\n",
        "Dunyoning eng qudratli harbiy ittifoqlari:\n"
    ]
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for idx, c in enumerate(top_clans):
        medal = medals[idx] if idx < len(medals) else f"#{idx+1}"
        lines.append(
            f"{medal} <b>{c.name}</b> [#{c.tag}] — Lv. {c.level}\n"
            f"   A'zolar: {len(c.members)} | 🏆 <b>{c.trophies}</b> kubok"
        )

    if not top_clans:
        lines.append("<i>Hozircha klanlar mavjud emas.</i>")

    text = "\n".join(lines)
    kb = get_leaderboard_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()
