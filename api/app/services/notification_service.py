import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.daily_session_repo import DailySessionRepository
from app.repositories.user_repo import UserRepository
from app.repositories.user_word_repo import UserWordRepository


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.user_word_repo = UserWordRepository(db)
        self.daily_session_repo = DailySessionRepository(db)

    async def get_pending_notifications(self) -> list[dict]:
        users = await self.user_repo.get_all_active()
        pending = []

        for user in users:
            try:
                tz = ZoneInfo(user.timezone)
            except (KeyError, Exception):
                tz = ZoneInfo("UTC")

            now_local = dt.datetime.now(tz)
            local_date = now_local.date()
            local_hour = now_local.hour

            if local_hour != user.daily_push_hour:
                continue

            if user.last_push_sent_date == local_date:
                continue

            due_count = await self.user_word_repo.get_due_count(user.id)
            session = await self.daily_session_repo.get_today_session(
                user.id, local_date
            )
            has_daily = session is not None and session.status == "completed"

            pending.append(
                {
                    "telegram_id": user.telegram_id,
                    "user_id": user.id,
                    "first_name": user.first_name,
                    "due_count": due_count,
                    "has_daily_session": has_daily,
                }
            )

        return pending

    async def mark_sent(self, user_ids: list[int]) -> int:
        count = 0
        for uid in user_ids:
            user = await self.user_repo.get_by_id(uid)
            if not user:
                continue
            try:
                tz = ZoneInfo(user.timezone)
            except (KeyError, Exception):
                tz = ZoneInfo("UTC")
            local_date = dt.datetime.now(tz).date()
            await self.user_repo.update(user, last_push_sent_date=local_date)
            count += 1
        return count
