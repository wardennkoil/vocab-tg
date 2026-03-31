import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.daily_session_repo import DailySessionRepository
from app.repositories.review_log_repo import ReviewLogRepository
from app.repositories.user_word_repo import UserWordRepository
from app.schemas.stats import DayStats, StatsHistory, StatsOverview

logger = logging.getLogger(__name__)


class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_word_repo = UserWordRepository(db)
        self.review_log_repo = ReviewLogRepository(db)
        self.daily_session_repo = DailySessionRepository(db)

    async def get_overview(self, user_id: int) -> StatsOverview:
        words_learning = await self.user_word_repo.count_by_status(user_id, "learning")
        words_custom = await self.user_word_repo.count_by_status(user_id, "custom")
        words_reviewing = await self.user_word_repo.count_by_status(user_id, "reviewing")
        words_known = await self.user_word_repo.count_by_status(user_id, "known")
        total = words_learning + words_custom + words_reviewing + words_known

        reviews_today = await self.review_log_repo.get_today_count(user_id)
        accuracy_rate = await self.review_log_repo.get_accuracy_rate(user_id)
        streak = await self._calculate_streak(user_id)

        due_tomorrow_count = await self.user_word_repo.get_due_count(user_id)

        return StatsOverview(
            total_words=total,
            words_learning=words_learning + words_custom + words_reviewing,
            words_known=words_known,
            current_streak=streak,
            accuracy_rate=accuracy_rate,
            reviews_today=reviews_today,
            due_tomorrow=due_tomorrow_count,
        )

    async def get_history(self, user_id: int, days: int = 30) -> StatsHistory:
        daily_counts = await self.review_log_repo.get_daily_counts(user_id, days)
        return StatsHistory(
            days=[
                DayStats(date=str(row[0]), review_count=row[1])
                for row in daily_counts
            ]
        )

    async def _calculate_streak(self, user_id: int) -> int:
        dates = await self.review_log_repo.get_dates_with_reviews(user_id)
        if not dates:
            return 0

        streak = 0
        today = datetime.now(timezone.utc).date()

        for i, review_date in enumerate(dates):
            expected = today - timedelta(days=i)
            if review_date == expected:
                streak += 1
            else:
                break

        return streak
