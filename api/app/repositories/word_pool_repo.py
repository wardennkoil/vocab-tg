from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.word import Word
from app.models.word_pool import WordPool
from app.repositories.base import BaseRepository


class WordPoolRepository(BaseRepository[WordPool]):
    def __init__(self, db: AsyncSession):
        super().__init__(WordPool, db)

    async def get_candidates(
        self,
        difficulty_band: str,
        exclude_word_ids: set[int],
        count: int = 12,
    ) -> list[WordPool]:
        query = (
            select(WordPool)
            .join(Word)
            .options(joinedload(WordPool.word))
            .where(Word.difficulty_band == difficulty_band)
        )
        if exclude_word_ids:
            query = query.where(WordPool.word_id.notin_(exclude_word_ids))

        query = query.order_by(func.random()).limit(count)
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def get_candidates_multi_difficulty(
        self,
        difficulty_bands: list[str],
        exclude_word_ids: set[int],
        count: int = 12,
    ) -> list[WordPool]:
        query = (
            select(WordPool)
            .join(Word)
            .options(joinedload(WordPool.word))
            .where(Word.difficulty_band.in_(difficulty_bands))
        )
        if exclude_word_ids:
            query = query.where(WordPool.word_id.notin_(exclude_word_ids))

        query = query.order_by(func.random()).limit(count)
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())

    async def count_by_source(self, source: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(WordPool).where(WordPool.source == source)
        )
        return result.scalar_one()
