from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.database import async_session_factory
from app.repositories.kingdom_repo import KingdomRepository
from app.repositories.battle_repo import BattleRepository
from app.services.battle_service import BattleService
from app.bot.keyboards.inline_keyboards import (
    get_battle_menu_keyboard,
    get_pve_campaigns_keyboard,
)

battle_router = Router()


@battle_router.message(F.text == "⚔️ Jang")
@battle_router.callback_query(F.data == "nav_battle")
async def view_battle_hub(event: Message | CallbackQuery):
    text = (
        "⚔️ <b>JANG MAYDONI VA ARENA</b>\n\n"
        "Shon-sharaf va behisob boyliklar uchun jangga kiring!\n\n"
        "• 👹 <b>PvE Kampaniyalar</b>: Goblinlar, Qaroqchilar va Qadimgi Ajdaho qal'alariga hujum qiling.\n"
        "• ⚔️ <b>PvP Arena</b>: Boshqa o'yinchilarning qirolliklariga zarba bering, kubok va resurslarni o'lja qiling!\n"
        "• 📜 <b>Janglar tarixi</b>: Oxirgi janglar tafsiloti."
    )
    kb = get_battle_menu_keyboard()
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await event.answer()


@battle_router.callback_query(F.data == "battle_pve_list")
async def cb_pve_list(callback: CallbackQuery):
    text = "👹 <b>PvE KAMPANIYALAR RO'YXATI</b>\n\nQuyidagi dushman qarorgohini tanlang va hujum boshlang:"
    kb = get_pve_campaigns_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@battle_router.callback_query(F.data.startswith("pve_fight_"))
async def cb_pve_fight(callback: CallbackQuery):
    user_id = callback.from_user.id
    campaign_id = int(callback.data.replace("pve_fight_", ""))

    async with async_session_factory() as session:
        service = BattleService(session)
        try:
            res = await service.fight_pve(user_id, campaign_id)
            await session.commit()
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

    outcome_emoji = "🏆 G'ALABA!" if res["is_winner"] else "💀 MAG'LUBIYAT!"
    loot = res["loot"]
    casualties_att = ", ".join([f"{k}: -{v}" for k, v in res["attacker_casualties"].items()]) or "Talafot yo'q"

    report = (
        f"⚔️ <b>JANG HISOBOTI: {res['campaign_name']}</b>\n"
        f"Natija: <b>{outcome_emoji}</b>\n"
        f"────────────────────\n"
        f"🩸 <b>Sizning talafotlaringiz:</b> {casualties_att}\n"
        f"💰 <b>Qo'lga kiritilgan o'lja:</b>\n"
        f"• 🪙 +{loot['gold']} Oltin\n"
        f"• 🪵 +{loot['wood']} Yog'och\n"
        f"• ⛏ +{loot['iron']} Temir\n"
        f"• 🌾 +{loot['food']} Oziq-ovqat\n"
        f"🏆 <b>Kuboklar:</b> +{res['trophies_delta']} (Jami: {res['current_trophies']})\n"
    )

    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Yana jangga kirish", callback_data="battle_pve_list")],
        [InlineKeyboardButton(text="🏰 Qirollikka qaytish", callback_data="act_refresh_kingdom")],
    ])

    try:
        await callback.message.edit_text(report, reply_markup=back_kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("Jang yakunlandi!")


@battle_router.callback_query(F.data == "battle_pvp_list")
async def cb_pvp_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session_factory() as session:
        repo = KingdomRepository(session)
        my_k = await repo.get_by_user_id(user_id)
        if not my_k:
            await callback.answer("Qirollik topilmadi!")
            return

        opponents = await repo.find_pvp_opponents(exclude_user_id=user_id, current_trophies=my_k.trophies, limit=5)

    if not opponents:
        text = "⚔️ <b>PvP ARENA</b>\n\nHozircha boshqa munosib raqiblar topilmadi. Birozdan so'ng qayta tekshiring!"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Jang menyusiga qaytish", callback_data="nav_battle")]
        ])
    else:
        text = "⚔️ <b>PvP ARENA: RAQIBLAR RO'YXATI</b>\n\nHujum qilish uchun raqib qirollikni tanlang:"
        buttons = []
        for opp in opponents:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🏰 {opp.name} (Lv.{opp.level} | 🏆 {opp.trophies})",
                    callback_data=f"pvp_fight_{opp.user_id}"
                )
            ])
        buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="nav_battle")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@battle_router.callback_query(F.data.startswith("pvp_fight_"))
async def cb_pvp_fight(callback: CallbackQuery):
    user_id = callback.from_user.id
    defender_id = int(callback.data.replace("pvp_fight_", ""))

    async with async_session_factory() as session:
        service = BattleService(session)
        try:
            res = await service.fight_pvp(user_id, defender_id)
            await session.commit()
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

    outcome_emoji = "🏆 G'ALABA!" if res["is_winner"] else "💀 MAG'LUBIYAT!"
    loot = res["loot"]
    casualties_att = ", ".join([f"{k}: -{v}" for k, v in res["attacker_casualties"].items()]) or "Talafot yo'q"
    casualties_def = ", ".join([f"{k}: -{v}" for k, v in res["defender_casualties"].items()]) or "Talafot yo'q"

    report = (
        f"⚔️ <b>PvP JANG HISOBOTI: {res['defender_name']}</b>\n"
        f"Natija: <b>{outcome_emoji}</b>\n"
        f"────────────────────\n"
        f"🩸 <b>Sizning talafotlaringiz:</b> {casualties_att}\n"
        f"💥 <b>Dushman talafotlari:</b> {casualties_def}\n"
        f"💰 <b>O'g'irlangan boyliklar:</b>\n"
        f"• 🪙 +{loot['gold']} Oltin | 🪵 +{loot['wood']} Yog'och\n"
        f"• ⛏ +{loot['iron']} Temir | 🌾 +{loot['food']} Oziq-ovqat\n"
        f"🏆 <b>Kuboklar o'zgarishi:</b> {res['trophies_delta']:+} (Hozirgi: {res['current_trophies']})\n"
    )

    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Arena ro'yxatiga qaytish", callback_data="battle_pvp_list")],
        [InlineKeyboardButton(text="🏰 Qirollikka qaytish", callback_data="act_refresh_kingdom")],
    ])

    try:
        await callback.message.edit_text(report, reply_markup=back_kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@battle_router.callback_query(F.data == "battle_history")
async def cb_battle_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session_factory() as session:
        repo = BattleRepository(session)
        battles = await repo.get_user_battle_history(user_id, limit=5)

    if not battles:
        text = "📜 <b>Janglar tarixi bo'sh.</b> Hali hech qanday jangga kirmadingiz."
    else:
        lines = ["📜 <b>SO'NGGI JANGLAR TARIXI:</b>\n"]
        for b in battles:
            res_str = "G'alaba 🟢" if (b.winner_id == user_id or b.is_attacker_winner) else "Mag'lubiyat 🔴"
            target = b.npc_name or f"Foydalanuvchi #{b.defender_id}"
            lines.append(
                f"• {b.created_at.strftime('%d.%m %H:%M')} — <b>{res_str}</b>\n"
                f"   Raqib: {target} | O'lja: +{b.loot_gold} 🪙 | Kubok: {b.trophies_delta:+}"
            )
        text = "\n".join(lines)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Jang menyusiga qaytish", callback_data="nav_battle")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()
