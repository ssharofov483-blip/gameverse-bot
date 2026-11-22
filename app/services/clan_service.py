from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.clan import Clan
from app.models.clan_member import ClanMember, ClanRole
from app.models.achievement import Achievement
from app.models.transaction import Transaction
from app.core.exceptions import (
    ClanException,
    InsufficientResourcesException,
    KingdomNotFoundException,
)
from app.repositories.clan_repo import ClanRepository
from app.repositories.kingdom_repo import KingdomRepository
from app.core.security import generate_idempotency_key


class ClanService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.clan_repo = ClanRepository(session)
        self.kingdom_repo = KingdomRepository(session)

    async def create_clan(self, user_id: int, name: str, tag: str, description: Optional[str] = None) -> Dict[str, Any]:
        existing_membership = await self.clan_repo.get_user_clan(user_id)
        if existing_membership:
            raise ClanException("Siz allaqachon boshqa klan a'zosisiz! Avval u yerdan chiqing.")

        # Tag format check
        clean_tag = tag.strip().upper().replace("#", "")
        if len(clean_tag) < 3 or len(clean_tag) > 8:
            raise ClanException("Klan tegi 3 dan 8 tagacha belgidan iborat bo'lishi kerak!")

        # Check unique name & tag
        if await self.clan_repo.get_by_name(name.strip()):
            raise ClanException("Bu nomdagi klan allaqachon mavjud!")
        if await self.clan_repo.get_by_tag(clean_tag):
            raise ClanException("Bu klan tegi allaqachon band qilingan!")

        # Deduct Clan creation fee (1000 Gold)
        kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not kingdom or not kingdom.resources:
            raise KingdomNotFoundException()

        if kingdom.resources.gold < 1000:
            raise InsufficientResourcesException("Klan yaratish uchun 1,000 oltin kerak!")

        kingdom.resources.gold -= 1000

        clan = Clan(
            name=name.strip(),
            tag=clean_tag,
            description=description or "Yangi jasur ritsarlar klani.",
            leader_id=user_id,
            level=1,
            trophies=kingdom.trophies,
            treasury_gold=250,
        )
        self.session.add(clan)
        await self.session.flush()

        member = ClanMember(
            clan_id=clan.id,
            user_id=user_id,
            role=ClanRole.LEADER.value,
            donated_gold=0,
        )
        self.session.add(member)

        # Audit tx
        self.session.add(Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key("clan_create"),
            category="CLAN_CREATION",
            gold_delta=-1000,
            details=f"'{clan.name}' [#{clan.tag}] klani tuzildi.",
        ))

        # Achievement
        ach = Achievement(
            user_id=user_id,
            code="CLAN_LEADER",
            title="Ittifoq Sardori 🤝",
            description="Yangi klan tuzib, o'z ittifoqingizga asos soldingiz.",
            reward_gold=2000,
        )
        self.session.add(ach)

        await self.session.flush()
        return {
            "clan_id": clan.id,
            "name": clan.name,
            "tag": clan.tag,
            "role": member.role,
        }

    async def join_clan(self, user_id: int, tag: str) -> Dict[str, Any]:
        existing_membership = await self.clan_repo.get_user_clan(user_id)
        if existing_membership:
            raise ClanException("Siz allaqachon klan a'zosisiz!")

        clean_tag = tag.strip().upper().replace("#", "")
        clan = await self.clan_repo.get_by_tag(clean_tag)
        if not clan:
            raise ClanException(f"#{clean_tag} tegli klan topilmadi!")

        member = ClanMember(
            clan_id=clan.id,
            user_id=user_id,
            role=ClanRole.MEMBER.value,
            donated_gold=0,
        )
        self.session.add(member)
        await self.session.flush()

        return {
            "clan_name": clan.name,
            "clan_tag": clan.tag,
            "role": member.role,
        }

    async def donate_to_treasury(self, user_id: int, amount: int) -> Dict[str, Any]:
        if amount <= 0:
            raise ClanException("Xayriya miqdori kamida 100 oltin bo'lishi kerak!")

        membership = await self.clan_repo.get_user_clan(user_id)
        if not membership:
            raise ClanException("Siz hech qaysi klan a'zosi emassiz!")

        clan, member = membership
        kingdom = await self.kingdom_repo.get_by_user_id(user_id)
        if not kingdom or not kingdom.resources:
            raise KingdomNotFoundException()

        if kingdom.resources.gold < amount:
            raise InsufficientResourcesException(f"Hisobingizda {amount} oltin mavjud emas!")

        kingdom.resources.gold -= amount
        clan.treasury_gold += amount
        member.donated_gold += amount

        # Clan leveling (every 10,000 gold = +1 clan level)
        new_level = 1 + (clan.treasury_gold // 10000)
        clan.level = new_level

        self.session.add(Transaction(
            user_id=user_id,
            idempotency_key=generate_idempotency_key("clan_don"),
            category="CLAN_DONATION",
            gold_delta=-amount,
            details=f"'{clan.name}' klan xazinasiga {amount} oltin xayriya qilindi.",
        ))

        await self.session.flush()
        return {
            "donated_amount": amount,
            "total_donated": member.donated_gold,
            "clan_treasury": clan.treasury_gold,
            "clan_level": clan.level,
        }
