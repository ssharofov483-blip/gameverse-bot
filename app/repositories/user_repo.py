from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == telegram_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "uz"
    ) -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.first_name = first_name
            user.username = username
            user.last_name = last_name
            user.last_active = datetime.now(timezone.utc)
            await self.session.flush()
            return user, False

        user = User(
            id=telegram_id,
            first_name=first_name,
            username=username,
            last_name=last_name,
            language_code=language_code,
            last_active=datetime.now(timezone.utc)
        )
        self.session.add(user)
        await self.session.flush()
        return user, True

    async def get_total_users_count(self) -> int:
        stmt = select(func.count(User.id))
        res = await self.session.execute(stmt)
        return res.scalar() or 0
