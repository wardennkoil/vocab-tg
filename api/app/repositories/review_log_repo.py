from datetime import datetime, timezone

from sqlalchemy import Date, Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review_log import ReviewLog
from app.repositories.base import BaseRepository


class ReviewLogRepository(BaseRepository[ReviewLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(ReviewLog, db)

    async def get_today_count(self, user_id: int) -> int:
        today = datetime.now(timezone.utc).date()
        result = await self.db.execute(
            select(func.count())
            .select_from(ReviewLog)
            .where(
                ReviewLog.user_id == user_id,
                cast(ReviewLog.reviewed_at, Date) == today,
            )
        )
        return result.scalar_one()

    async def get_accuracy_rate(self, user_id: int) -> float | None:
        result = await self.db.execute(
            select(func.avg(cast(ReviewLog.was_correct, Integer)))
            .where(
                ReviewLog.user_id == user_id,
                ReviewLog.was_correct.isnot(None),
            )
        )
        val = result.scalar_one()
        return float(val) if val is not None else None

    async def get_daily_counts(self, user_id: int, days: int = 30) -> list[tuple]:
        result = await self.db.execute(
            select(
                cast(ReviewLog.reviewed_at, Date).label("day"),
                func.count().label("count"),
            )
            .where(ReviewLog.user_id == user_id)
            .group_by("day")
            .order_by("day")
            .limit(days)
        )
        return list(result.all())

    async def get_dates_with_reviews(self, user_id: int) -> list[datetime]:
        result = await self.db.execute(
            select(cast(ReviewLog.reviewed_at, Date).distinct())
            .where(ReviewLog.user_id == user_id)
            .order_by(cast(ReviewLog.reviewed_at, Date).desc())
        )
        return list(result.scalars().all())
