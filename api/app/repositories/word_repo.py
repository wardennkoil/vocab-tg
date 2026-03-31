from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.word import Word
from app.repositories.base import BaseRepository


class WordRepository(BaseRepository[Word]):
    def __init__(self, db: AsyncSession):
        super().__init__(Word, db)

    async def get_by_word(self, word: str) -> Word | None:
        result = await self.db.execute(
            select(Word).where(Word.word == word.lower())
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, word: str) -> tuple[Word, bool]:
        existing = await self.get_by_word(word.lower())
        if existing:
            return existing, False
        new_word = await self.create(word=word.lower())
        return new_word, True

    async def get_unenriched(self, limit: int = 50) -> list[Word]:
        result = await self.db.execute(
            select(Word)
            .where(Word.is_enriched == False)  # noqa: E712
            .limit(limit)
        )
        return list(result.scalars().all())
