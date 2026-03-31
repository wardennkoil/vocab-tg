from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def get_active_users_for_daily_push(self, current_hour: int, timezones: list[str]) -> list[User]:
        result = await self.db.execute(
            select(User).where(
                User.is_active == True,  # noqa: E712
                User.daily_push_hour == current_hour,
                User.timezone.in_(timezones),
            )
        )
        return list(result.scalars().all())

    async def upsert_from_telegram(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return await self.update(
                user,
                username=username or user.username,
                first_name=first_name or user.first_name,
                language_code=language_code or user.language_code,
            )
        return await self.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language_code=language_code or "en",
        )
