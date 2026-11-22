from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.core.database import async_session_factory
from app.repositories.kingdom_repo import KingdomRepository
from app.services.troop_service import TroopService
from app.engine.constants import TROOP_CONFIG
from app.models.building import BuildingType
from app.bot.keyboards.inline_keyboards import get_troops_recruit_keyboard

troops_router = Router()


def format_troops_overview(kingdom) -> str:
    barracks = next((b for b in kingdom.buildings if b.building_type == BuildingType.BARRACKS.value), None)
    barracks_lvl = barracks.level if barracks else 1
    max_cap = barracks_lvl * 100
    total_army = sum(t.count for t in kingdom.troops)

    lines = [
        "🪖 <b>QIROLLIK QO‘SHINI VA KAZARMA</b>\n",
        f"Kazarma darajasi: <b>Lv. {barracks_lvl}</b>",
        f"Jami askarlar: <b>{total_army} / {max_cap}</b>\n",
        "<b>Mavjud bo'linmalar:</b>"
    ]

    for t_type, cfg in TROOP_CONFIG.items():
        count = next((t.count for t in kingdom.troops if t.troop_type == t_type), 0)
        lines.append(
            f"• <b>{cfg['name_uz']}</b>: {count} ta "
            f"<i>(⚔️ {cfg['attack']} | 🛡 {cfg['defense']} | ❤️ {cfg['hp']})</i>\n"
            f"   1 ta narxi: 🪙 {cfg['cost_gold']} | 🪵 {cfg['cost_wood']} | ⛏ {cfg['cost_iron']} | 🌾 {cfg['cost_food']}"
        )

    lines.append("\n<i>Quyidagi tugmalar orqali yangi jangchilarni yollang:</i>")
    return "\n".join(lines)


@troops_router.message(F.text == "🪖 Qo‘shin")
@troops_router.callback_query(F.data == "nav_troops")
async def view_troops(event: Message | CallbackQuery):
    user_id = event.from_user.id
    async with async_session_factory() as session:
        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        if not kingdom:
            await (event.answer("Avval /start bosing!") if isinstance(event, Message) else event.answer())
            return

        text = format_troops_overview(kingdom)
        kb = get_troops_recruit_keyboard()

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await event.answer()


@troops_router.callback_query(F.data.startswith("rec_"))
async def cb_recruit_troops(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Format: rec_{troop_type}_{count}
    parts = callback.data.split("_")
    troop_type = parts[1]
    count = int(parts[2])

    async with async_session_factory() as session:
        service = TroopService(session)
        try:
            res = await service.recruit_troops(user_id, troop_type, count)
            await session.commit()
            await callback.answer(
                f"+{count} ta {troop_type} yollangan! Jami: {res['total_count']} ta.",
                show_alert=True
            )
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        text = format_troops_overview(kingdom)
        kb = get_troops_recruit_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
