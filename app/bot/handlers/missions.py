from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.core.database import async_session_factory
from app.services.mission_service import MissionService
from app.bot.keyboards.inline_keyboards import get_missions_keyboard

missions_router = Router()


def format_missions_text(missions) -> str:
    lines = [
        "📜 <b>KUNDALIK MISSIYALAR VA TOPSHIRIQLAR</b>\n",
        "Har kuni yangilanadigan topshiriqlarni bajaring va boy mukofotlarni qo'lga kiriting:\n"
    ]
    for m in missions:
        status_icon = "✅" if m.is_claimed else ("🎁" if m.is_completed else "⏳")
        status_text = "Qabul qilingan" if m.is_claimed else ("Tayyor! Oling" if m.is_completed else f"{m.current_count}/{m.target_count}")
        lines.append(
            f"{status_icon} <b>{m.title}</b> [{status_text}]\n"
            f"   <i>{m.description}</i>\n"
            f"   Mukofot: 🪙 +{m.reward_gold} | 🪵 +{m.reward_wood} | ⛏ +{m.reward_iron}\n"
        )
    return "\n".join(lines)


@missions_router.message(F.text == "📜 Missiyalar")
@missions_router.callback_query(F.data == "nav_missions")
async def view_missions(event: Message | CallbackQuery):
    user_id = event.from_user.id
    async with async_session_factory() as session:
        service = MissionService(session)
        missions = await service.get_daily_missions(user_id)
        await session.commit()
        text = format_missions_text(missions)
        kb = get_missions_keyboard(missions)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await event.answer()


@missions_router.callback_query(F.data.startswith("claim_m_"))
async def cb_claim_mission(callback: CallbackQuery):
    user_id = callback.from_user.id
    mission_id = int(callback.data.replace("claim_m_", ""))

    async with async_session_factory() as session:
        service = MissionService(session)
        try:
            res = await service.claim_mission(user_id, mission_id)
            await session.commit()
            await callback.answer(
                f"Mukofot olindi! +{res['reward_gold']} 🪙, +{res['reward_wood']} 🪵, +{res['reward_iron']} ⛏",
                show_alert=True
            )
        except Exception as e:
            await callback.answer(f"Xatolik: {str(e)}", show_alert=True)
            return

        missions = await service.get_daily_missions(user_id)
        text = format_missions_text(missions)
        kb = get_missions_keyboard(missions)

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
