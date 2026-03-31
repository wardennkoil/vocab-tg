from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.user_word import UserWord
from app.repositories.base import BaseRepository


class UserWordRepository(BaseRepository[UserWord]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserWord, db)

    async def get_by_user_and_word(self, user_id: int, word_id: int) -> UserWord | None:
        result = await self.db.execute(
            select(UserWord)
            .options(joinedload(UserWord.word))
            .where(
                UserWord.user_id == user_id,
                UserWord.word_id == word_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_word_ids(self, user_id: int) -> set[int]:
        result = await self.db.execute(
            select(UserWord.word_id).where(UserWord.user_id == user_id)
        )
        return set(result.scalars().all())

    async def get_due_words(self, user_id: int) -> list[UserWord]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(UserWord)
            .options(joinedload(UserWord.word))
            .where(
                UserWord.user_id == user_id,
                UserWord.due_at <= now,
                UserWord.status.in_(["learning", "reviewing", "custom"]),
            )
            .order_by(UserWord.due_at)
        )
        return list(result.scalars().unique().all())

    async def get_due_count(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(func.count())
            .select_from(UserWord)
            .where(
                UserWord.user_id == user_id,
                UserWord.due_at <= now,
                UserWord.status.in_(["learning", "reviewing", "custom"]),
            )
        )
        return result.scalar_one()

    async def get_user_words_paginated(
        self,
        user_id: int,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[UserWord], int]:
        query = (
            select(UserWord)
            .options(joinedload(UserWord.word))
            .where(UserWord.user_id == user_id)
        )
        count_query = (
            select(func.count())
            .select_from(UserWord)
            .where(UserWord.user_id == user_id)
        )

        if status:
            query = query.where(UserWord.status == status)
            count_query = count_query.where(UserWord.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        result = await self.db.execute(
            query.order_by(UserWord.added_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        items = list(result.scalars().unique().all())
        return items, total

    async def count_by_status(self, user_id: int, status: str) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(UserWord)
            .where(UserWord.user_id == user_id, UserWord.status == status)
        )
        return result.scalar_one()
