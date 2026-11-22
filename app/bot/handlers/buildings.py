from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.core.database import async_session_factory
from app.repositories.kingdom_repo import KingdomRepository
from app.services.kingdom_service import KingdomService
from app.engine.economy import EconomyEngine
from app.engine.constants import BUILDING_CONFIG
from app.bot.keyboards.inline_keyboards import get_buildings_keyboard

buildings_router = Router()


def format_buildings_overview(kingdom) -> str:
    lines = [
        "🏗 <b>QIROLLIK BINOLARI VA QURILISH</b>\n",
        "Binolarni yangilash orqali ishlab chiqarish, qo'shin sig'imi va mudofaangizni oshiring:\n"
    ]
    for b in kingdom.buildings:
        cfg = BUILDING_CONFIG.get(b.building_type, {})
        name = cfg.get("name_uz", b.building_type)
        cost = EconomyEngine.get_building_upgrade_cost(b.building_type, b.level)
        lines.append(
            f"• <b>{name}</b> — <b>Lv. {b.level}</b>\n"
            f"   Keyingi bosqich narxi: 🪙 {cost['gold']:,} | 🪵 {cost['wood']:,} | ⛏ {cost['iron']:,}"
        )
    lines.append("\n<i>Quyidagi tugmalar orqali binoni yangilang:</i>")
    return "\n".join(lines)


@buildings_router.message(F.text == "🏗 Qurilish")
@buildings_router.callback_query(F.data == "nav_buildings")
async def view_buildings(event: Message | CallbackQuery):
    user_id = event.from_user.id
    async with async_session_factory() as session:
        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        if not kingdom:
            await (event.answer("Avval /start bosing!") if isinstance(event, Message) else event.answer())
            return

        text = format_buildings_overview(kingdom)
        kb = get_buildings_keyboard(kingdom.buildings)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await event.answer()


@buildings_router.callback_query(F.data.startswith("upg_b_"))
async def cb_upgrade_building(callback: CallbackQuery):
    user_id = callback.from_user.id
    building_type = callback.data.replace("upg_b_", "")

    async with async_session_factory() as session:
        service = KingdomService(session)
        try:
            res = await service.upgrade_building(user_id, building_type)
            await session.commit()
            msg = f"Bino {res['new_level']}-bosqichga ko'tarildi! (+{res['xp_gained']} XP)"
            if res.get("leveled_up"):
                msg += f"\nTabriklaymiz! Qirollik {res['kingdom_level']}-darajaga ko'tarildi! 🎉"
            await callback.answer(msg, show_alert=True)
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        text = format_buildings_overview(kingdom)
        kb = get_buildings_keyboard(kingdom.buildings)

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
