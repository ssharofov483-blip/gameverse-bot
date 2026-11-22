from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.mission import Mission
from app.engine.progression import DEFAULT_MISSIONS
from app.repositories.base_repo import BaseRepository


class MissionRepository(BaseRepository[Mission]):
    def __init__(self, session: AsyncSession):
        super().__init__(Mission, session)

    async def get_or_generate_daily_missions(self, user_id: int) -> List[Mission]:
        now = datetime.now(timezone.utc)
        stmt = select(Mission).where(Mission.user_id == user_id, Mission.expires_at > now)
        res = await self.session.execute(stmt)
        active_missions = list(res.scalars().all())

        if active_missions:
            return active_missions

        # Generate fresh daily missions expiring at midnight / 24 hours
        expires_at = now + timedelta(days=1)
        created = []
        for d in DEFAULT_MISSIONS:
            m = Mission(
                user_id=user_id,
                mission_key=d["mission_key"],
                title=d["title"],
                description=d["description"],
                target_count=d["target_count"],
                current_count=0,
                reward_gold=d["reward_gold"],
                reward_wood=d["reward_wood"],
                reward_iron=d["reward_iron"],
                is_completed=False,
                is_claimed=False,
                expires_at=expires_at,
            )
            self.session.add(m)
            created.append(m)

        await self.session.flush()
        return created

    async def increment_mission_progress(self, user_id: int, mission_key: str, amount: int = 1) -> None:
        now = datetime.now(timezone.utc)
        stmt = select(Mission).where(
            Mission.user_id == user_id,
            Mission.mission_key == mission_key,
            Mission.expires_at > now,
            Mission.is_completed == False  # noqa: E712
        )
        res = await self.session.execute(stmt)
        mission = res.scalar_one_or_none()
        if mission:
            mission.current_count += amount
            if mission.current_count >= mission.target_count:
                mission.current_count = mission.target_count
                mission.is_completed = True
            await self.session.flush()
