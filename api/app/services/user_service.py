from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserSettingsUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        return await self.repo.upsert_from_telegram(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language_code=language_code,
        )

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def update_settings(self, user: User, settings: UserSettingsUpdate) -> User:
        update_data = settings.model_dump(exclude_none=True)
        if not update_data:
            return user
        return await self.repo.update(user, **update_data)
