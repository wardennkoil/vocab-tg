import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_word import UserWord
from app.models.word import Word
from app.repositories.user_word_repo import UserWordRepository
from app.repositories.word_repo import WordRepository
from app.schemas.word import WordCard
from app.services.datamuse_service import DatamuseService
from app.services.datamuse_service import WordSuggestion as DatamuseSuggestion
from app.services.dictionary_service import DictionaryService
from app.services.translation_service import TranslationService
from app.utils.fsrs_helper import create_new_card

logger = logging.getLogger(__name__)


class WordService:
    def __init__(
        self,
        db: AsyncSession,
        http_client: httpx.AsyncClient,
        translation_service: TranslationService,
    ):
        self.db = db
        self.word_repo = WordRepository(db)
        self.user_word_repo = UserWordRepository(db)
        self.dictionary_service = DictionaryService(http_client)
        self.datamuse_service = DatamuseService(http_client)
        self.translation_service = translation_service

    async def get_or_enrich_word(self, word_text: str) -> Word:
        word, created = await self.word_repo.get_or_create(word_text)

        if not word.is_enriched:
            defn = await self.dictionary_service.lookup(word_text)
            if defn:
                translation = await self.translation_service.translate_to_russian(word_text)
                await self.word_repo.update(
                    word,
                    phonetic=defn.phonetic,
                    audio_url=defn.audio_url,
                    definition=defn.definition,
                    definitions_json=defn.definitions,
                    example_sentence=defn.example,
                    synonyms=defn.synonyms,
                    antonyms=defn.antonyms,
                    part_of_speech=defn.part_of_speech,
                    translation_ru=translation,
                    is_enriched=True,
                    enriched_at=datetime.now(timezone.utc),
                )
            else:
                translation = await self.translation_service.translate_to_russian(word_text)
                await self.word_repo.update(
                    word,
                    translation_ru=translation,
                    is_enriched=True,
                    enriched_at=datetime.now(timezone.utc),
                )
        elif word.translation_ru is None:
            translation = await self.translation_service.translate_to_russian(word_text)
            if translation:
                await self.word_repo.update(word, translation_ru=translation)

        return word

    def word_to_card(self, word: Word) -> WordCard:
        return WordCard.model_validate(word)

    async def get_word_card(self, word_text: str) -> WordCard:
        word = await self.get_or_enrich_word(word_text)
        return self.word_to_card(word)

    async def add_custom_word(self, user_id: int, word_text: str) -> UserWord:
        word = await self.get_or_enrich_word(word_text)

        existing = await self.user_word_repo.get_by_user_and_word(user_id, word.id)
        if existing:
            return existing

        fsrs_card = create_new_card()
        user_word = await self.user_word_repo.create(
            user_id=user_id,
            word_id=word.id,
            status="custom",
            source="custom",
            fsrs_card_json=fsrs_card,
            due_at=datetime.now(timezone.utc),
        )
        # Re-query with word relationship loaded
        return await self.user_word_repo.get_by_user_and_word(user_id, word.id)

    async def get_user_words(
        self,
        user_id: int,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[UserWord], int]:
        return await self.user_word_repo.get_user_words_paginated(
            user_id, status=status, page=page, per_page=per_page
        )

    async def remove_user_word(self, user_id: int, user_word_id: int) -> bool:
        user_word = await self.user_word_repo.get_by_id(user_word_id)
        if not user_word or user_word.user_id != user_id:
            return False
        await self.user_word_repo.delete(user_word)
        return True

    async def suggest_words(self, prefix: str) -> list[DatamuseSuggestion]:
        return await self.datamuse_service.suggest(prefix)
