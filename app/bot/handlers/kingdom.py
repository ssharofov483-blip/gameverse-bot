from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.core.database import async_session_factory
from app.repositories.kingdom_repo import KingdomRepository
from app.services.kingdom_service import KingdomService
from app.engine.economy import EconomyEngine
from app.bot.keyboards.inline_keyboards import get_kingdom_actions_keyboard

kingdom_router = Router()


def format_kingdom_message(kingdom) -> str:
    res = kingdom.resources
    rates = EconomyEngine.calculate_hourly_production(kingdom.buildings)
    pending, elapsed = EconomyEngine.calculate_pending_resources(res, kingdom.buildings)

    total_army = sum(t.count for t in kingdom.troops)

    text = (
        f"🏰 <b>{kingdom.name}</b> (Daraja: <b>{kingdom.level}</b>)\n"
        f"🏆 <b>Kuboklar:</b> {kingdom.trophies} | 🎖 <b>XP:</b> {kingdom.experience}\n"
        f"⚔️ <b>Jami qo'shin:</b> {total_army} ta jangchi\n"
        f"────────────────────\n"
        f"💰 <b>Resurslar ombori:</b> (Maks: {res.max_capacity:,})\n"
        f"• 🪙 Oltin: <b>{res.gold:,}</b> <i>(+{rates['gold']}/soat)</i>\n"
        f"• 🪵 Yog'och: <b>{res.wood:,}</b> <i>(+{rates['wood']}/soat)</i>\n"
        f"• ⛏ Temir: <b>{res.iron:,}</b> <i>(+{rates['iron']}/soat)</i>\n"
        f"• 🌾 Oziq-ovqat: <b>{res.food:,}</b> <i>(+{rates['food']}/soat)</i>\n"
        f"────────────────────\n"
        f"⏳ <b>Yig'ishga tayyor:</b>\n"
        f"🪙 +{pending['gold']} | 🪵 +{pending['wood']} | ⛏ +{pending['iron']} | 🌾 +{pending['food']}\n"
    )
    return text


@kingdom_router.message(F.text == "🏰 Mening qirolligim")
async def view_kingdom(message: Message):
    user_id = message.from_user.id
    async with async_session_factory() as session:
        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        if not kingdom:
            await message.answer("Avval /start buyrug'ini yuboring!")
            return

        text = format_kingdom_message(kingdom)

    await message.answer(
        text,
        reply_markup=get_kingdom_actions_keyboard(),
        parse_mode="HTML"
    )


@kingdom_router.callback_query(F.data == "act_collect_res")
async def cb_collect_resources(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session_factory() as session:
        service = KingdomService(session)
        try:
            result = await service.collect_resources(user_id)
            await session.commit()
            gained = result["gained"]
            await callback.answer(
                f"Yig'ildi: +{gained['gold']} 🪙, +{gained['wood']} 🪵, +{gained['iron']} ⛏, +{gained['food']} 🌾",
                show_alert=True
            )
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

        # Refresh view
        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        text = format_kingdom_message(kingdom)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_kingdom_actions_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        pass


@kingdom_router.callback_query(F.data == "act_refresh_kingdom")
async def cb_refresh_kingdom(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session_factory() as session:
        repo = KingdomRepository(session)
        kingdom = await repo.get_by_user_id(user_id)
        text = format_kingdom_message(kingdom)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_kingdom_actions_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("Yangilandi!")
