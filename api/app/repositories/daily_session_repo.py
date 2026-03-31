import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_session import DailySession
from app.repositories.base import BaseRepository


class DailySessionRepository(BaseRepository[DailySession]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailySession, db)

    async def get_today_session(self, user_id: int, today: dt.date | None = None) -> DailySession | None:
        if today is None:
            today = dt.date.today()
        result = await self.db.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.session_date == today,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_today(self, user_id: int, today: dt.date | None = None) -> tuple[DailySession, bool]:
        if today is None:
            today = dt.date.today()
        existing = await self.get_today_session(user_id, today)
        if existing:
            return existing, False
        session = await self.create(user_id=user_id, session_date=today)
        return session, True

    async def count_completed(self, user_id: int) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count())
            .select_from(DailySession)
            .where(
                DailySession.user_id == user_id,
                DailySession.status == "completed",
            )
        )
        return result.scalar_one()
