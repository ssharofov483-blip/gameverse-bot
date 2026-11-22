from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import async_session_factory
from app.models.user import User
from app.repositories.kingdom_repo import KingdomRepository
from app.repositories.battle_repo import BattleRepository

profile_router = Router()


@profile_router.message(F.text == "👤 Profil")
async def view_profile(message: Message):
    user_id = message.from_user.id
    async with async_session_factory() as session:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.achievements),
                selectinload(User.inventory)
            )
        )
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()

        k_repo = KingdomRepository(session)
        kingdom = await k_repo.get_by_user_id(user_id)

        b_repo = BattleRepository(session)
        battles = await b_repo.get_user_battle_history(user_id, limit=50)

    if not user or not kingdom:
        await message.answer("Avval /start bosing!")
        return

    wins = sum(1 for b in battles if b.winner_id == user_id or (b.attacker_id == user_id and b.is_attacker_winner))
    total_battles = len(battles)

    ach_lines = []
    for a in user.achievements:
        ach_lines.append(f"• {a.title} <i>({a.description})</i>")
    ach_text = "\n".join(ach_lines) if ach_lines else "<i>Hozircha yutuqlar yo'q.</i>"

    text = (
        f"👤 <b>HUKMDOR PROFILI</b>\n"
        f"Ism: <b>{user.first_name}</b> (@{user.username or 'mavjud_emas'})\n"
        f"ID: <code>{user.id}</code>\n"
        f"Ro'yxatdan o'tgan sana: {user.created_at.strftime('%d.%m.%Y')}\n"
        f"────────────────────\n"
        f"🏰 Qirollik: <b>{kingdom.name}</b> (Lv. {kingdom.level})\n"
        f"🏆 Kuboklar: <b>{kingdom.trophies}</b>\n"
        f"⚔️ Janglar statistikasi: <b>{wins} G'alaba</b> / {total_battles} Jang\n"
        f"────────────────────\n"
        f"🎖 <b>Qo'lga kiritilgan yutuqlar ({len(user.achievements)}):</b>\n"
        f"{ach_text}"
    )

    await message.answer(text, parse_mode="HTML")


@profile_router.message(F.text == "🎒 Inventar")
async def view_inventory(message: Message):
    user_id = message.from_user.id
    async with async_session_factory() as session:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.inventory))
        )
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()

    if not user:
        await message.answer("Avval /start bosing!")
        return

    if not user.inventory:
        text = (
            "🎒 <b>QIROLLIK INVENTARI</b>\n\n"
            "Hozircha sizda qadimiy qurol-aslahalar va artefaktlar mavjud emas.\n\n"
            "<i>PvE qasrlariga hujum qilib yoki ajdahoni mag'lub etib kamyob buyumlarni qo'lga kiritishingiz mumkin!</i>"
        )
    else:
        lines = ["🎒 <b>QIROLLIK INVENTARI VA ARTEFAKTLAR:</b>\n"]
        for it in user.inventory:
            eq = "✅ [Taqilgan]" if it.is_equipped else ""
            lines.append(f"• <b>{it.name}</b> ({it.rarity.upper()}) {eq}\n   ⚔️ +{it.attack_bonus} Hujum | 🛡 +{it.defense_bonus} Himoya")
        text = "\n".join(lines)

    await message.answer(text, parse_mode="HTML")
