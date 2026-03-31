import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_word import UserWord
from app.repositories.daily_session_repo import DailySessionRepository
from app.repositories.user_word_repo import UserWordRepository
from app.repositories.word_pool_repo import WordPoolRepository
from app.repositories.word_repo import WordRepository
from app.schemas.daily import DailyWordsResponse, TriageCandidate, TriageCandidatesResponse
from app.schemas.word import WordCard
from app.services.word_service import WordService
from app.utils.fsrs_helper import create_new_card

logger = logging.getLogger(__name__)


class DailyService:
    def __init__(self, db: AsyncSession, word_service: WordService):
        self.db = db
        self.word_service = word_service
        self.user_word_repo = UserWordRepository(db)
        self.word_pool_repo = WordPoolRepository(db)
        self.word_repo = WordRepository(db)
        self.daily_session_repo = DailySessionRepository(db)

    async def generate_triage_candidates(
        self, user: User, count: int = 12
    ) -> TriageCandidatesResponse:
        session, _ = await self.daily_session_repo.get_or_create_today(user.id)

        if session.triage_word_ids:
            candidates = []
            for wid in session.triage_word_ids:
                word = await self.word_repo.get_by_id(wid)
                if word:
                    candidates.append(
                        TriageCandidate(
                            word_id=word.id,
                            word=word.word,
                            definition=word.definition,
                        )
                    )
            return TriageCandidatesResponse(
                candidates=candidates, session_id=session.id
            )

        exclude_ids = await self.user_word_repo.get_user_word_ids(user.id)

        difficulty_bands = self._get_difficulty_bands(user.difficulty_level)
        pool_entries = await self.word_pool_repo.get_candidates_multi_difficulty(
            difficulty_bands=difficulty_bands,
            exclude_word_ids=exclude_ids,
            count=count,
        )

        candidates = []
        triage_word_ids = []
        for entry in pool_entries:
            word = entry.word
            if not word.is_enriched:
                word = await self.word_service.get_or_enrich_word(word.word)
            candidates.append(
                TriageCandidate(
                    word_id=word.id,
                    word=word.word,
                    definition=word.definition,
                )
            )
            triage_word_ids.append(word.id)

        await self.daily_session_repo.update(
            session,
            triage_word_ids=triage_word_ids,
            status="triage_in_progress",
        )

        return TriageCandidatesResponse(
            candidates=candidates, session_id=session.id
        )

    async def submit_triage(
        self,
        user: User,
        session_id: int,
        known_word_ids: list[int],
        unknown_word_ids: list[int],
    ) -> list[WordCard]:
        session = await self.daily_session_repo.get_by_id(session_id)
        if not session or session.user_id != user.id:
            return []

        for wid in known_word_ids:
            existing = await self.user_word_repo.get_by_user_and_word(user.id, wid)
            if not existing:
                await self.user_word_repo.create(
                    user_id=user.id,
                    word_id=wid,
                    status="known",
                    source="triage_known",
                )

        daily_words = []
        daily_count = min(len(unknown_word_ids), user.daily_word_count)
        for wid in unknown_word_ids[:daily_count]:
            word = await self.word_service.get_or_enrich_word(
                (await self.word_repo.get_by_id(wid)).word
            )
            existing = await self.user_word_repo.get_by_user_and_word(user.id, wid)
            if not existing:
                fsrs_card = create_new_card()
                await self.user_word_repo.create(
                    user_id=user.id,
                    word_id=wid,
                    status="learning",
                    source="daily",
                    fsrs_card_json=fsrs_card,
                    due_at=datetime.now(timezone.utc),
                )
            daily_words.append(self.word_service.word_to_card(word))

        await self.daily_session_repo.update(
            session,
            known_word_ids=known_word_ids,
            selected_word_ids=unknown_word_ids[:daily_count],
            daily_word_ids=[w.id for w in daily_words],
            status="completed",
        )

        return daily_words

    async def auto_select_daily(self, user: User) -> list[WordCard]:
        session, created = await self.daily_session_repo.get_or_create_today(user.id)
        if not created and session.status == "completed" and session.daily_word_ids:
            return await self._get_words_by_ids(session.daily_word_ids)

        exclude_ids = await self.user_word_repo.get_user_word_ids(user.id)
        difficulty_bands = self._get_difficulty_bands(user.difficulty_level)
        pool_entries = await self.word_pool_repo.get_candidates_multi_difficulty(
            difficulty_bands=difficulty_bands,
            exclude_word_ids=exclude_ids,
            count=user.daily_word_count,
        )

        daily_words = []
        daily_word_ids = []
        for entry in pool_entries:
            word = await self.word_service.get_or_enrich_word(entry.word.word)
            fsrs_card = create_new_card()
            await self.user_word_repo.create(
                user_id=user.id,
                word_id=word.id,
                status="learning",
                source="daily",
                fsrs_card_json=fsrs_card,
                due_at=datetime.now(timezone.utc),
            )
            daily_words.append(self.word_service.word_to_card(word))
            daily_word_ids.append(word.id)

        await self.daily_session_repo.update(
            session,
            daily_word_ids=daily_word_ids,
            status="completed",
        )

        return daily_words

    async def get_today_words(self, user: User) -> DailyWordsResponse:
        session = await self.daily_session_repo.get_today_session(user.id)
        if not session or not session.daily_word_ids:
            return DailyWordsResponse(
                words=[],
                session_date=str(datetime.now(timezone.utc).date()),
                status="no_session",
            )

        words = await self._get_words_by_ids(session.daily_word_ids)
        return DailyWordsResponse(
            words=words,
            session_date=str(session.session_date),
            status=session.status,
        )

    async def _get_words_by_ids(self, word_ids: list[int]) -> list[WordCard]:
        cards = []
        for wid in word_ids:
            word = await self.word_repo.get_by_id(wid)
            if word:
                cards.append(self.word_service.word_to_card(word))
        return cards

    def _get_difficulty_bands(self, difficulty_level: str) -> list[str]:
        if difficulty_level == "C1-C2":
            return ["C1-C2", "B2-C1"]
        elif difficulty_level == "B2-C1":
            return ["B2-C1", "C1-C2"]
        elif difficulty_level == "B1-B2":
            return ["B1-B2", "B2-C1"]
        return ["B2-C1", "C1-C2"]
