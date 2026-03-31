import logging
import random
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.review_log_repo import ReviewLogRepository
from app.repositories.user_word_repo import UserWordRepository
from app.repositories.word_repo import WordRepository
from app.schemas.review import ReviewItem, ReviewResult, ReviewSession
from app.schemas.word import WordCard
from app.services.review_generators import (
    build_fill_blank_mcq_item,
    build_fill_blank_type_item,
    build_matching_item,
    build_mcq_item,
    build_odd_one_out_item,
    build_reverse_mcq_item,
    build_true_false_item,
    build_word_in_context_item,
    sample_distractors,
)
from app.services.review_type_selector import select_review_type
from app.utils.fsrs_helper import review_card

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_word_repo = UserWordRepository(db)
        self.review_log_repo = ReviewLogRepository(db)
        self.word_repo = WordRepository(db)

    async def get_due_count(self, user_id: int) -> int:
        return await self.user_word_repo.get_due_count(user_id)

    async def create_review_session(
        self, user: User, exclude_types: list[str] | None = None,
    ) -> ReviewSession:
        due_words = await self.user_word_repo.get_due_words(user.id)
        if not due_words:
            return ReviewSession(items=[], total=0, due_count=0)

        all_user_words = (
            await self.user_word_repo.get_user_words_paginated(
                user.id, per_page=200
            )
        )[0]

        pool = [
            WordCard.model_validate(uw.word)
            for uw in all_user_words
            if uw.word
        ]
        exclude = set(exclude_types or [])

        items: list[ReviewItem] = []
        due_queue = list(due_words)
        random.shuffle(due_queue)
        consumed_ids: set[int] = set()
        total_word_reviews = 0

        # Try to form matching groups (~15% chance per eligible batch of 4-5)
        if "matching" not in exclude:
            matching_candidates = [
                uw
                for uw in due_queue
                if uw.word
                and (uw.word.definition or uw.word.translation_ru)
            ]
            i = 0
            while i + 3 < len(matching_candidates):
                if random.random() < 0.15:
                    batch_size = min(
                        random.choice([4, 5]),
                        len(matching_candidates) - i,
                    )
                    batch = matching_candidates[i : i + batch_size]
                    word_pairs = [
                        (uw.id, WordCard.model_validate(uw.word))
                        for uw in batch
                    ]
                    items.append(build_matching_item(word_pairs))
                    for uw in batch:
                        consumed_ids.add(uw.id)
                    total_word_reviews += batch_size
                    i += batch_size
                else:
                    i += 1

        # Assign individual types to remaining words
        for uw in due_queue:
            if uw.id in consumed_ids:
                continue
            word_card = WordCard.model_validate(uw.word)
            has_synonyms = len(word_card.synonyms) >= 2

            review_type = select_review_type(word_card, has_synonyms)

            # Re-roll if excluded type
            attempts = 0
            while review_type in exclude and attempts < 10:
                review_type = select_review_type(word_card, has_synonyms)
                attempts += 1
            if review_type in exclude:
                review_type = "multiple_choice"

            item = self._build_item(
                review_type, word_card, uw.id, pool
            )
            items.append(item)
            total_word_reviews += 1

        random.shuffle(items)
        return ReviewSession(
            items=items,
            total=total_word_reviews,
            due_count=len(due_words),
        )

    def _build_item(
        self,
        review_type: str,
        word: WordCard,
        user_word_id: int,
        pool: list[WordCard],
    ) -> ReviewItem:
        if review_type == "multiple_choice":
            return build_mcq_item(word, user_word_id, pool)
        elif review_type == "reverse_mcq":
            return build_reverse_mcq_item(word, user_word_id, pool)
        elif review_type == "fill_blank_mcq":
            return build_fill_blank_mcq_item(word, user_word_id, pool)
        elif review_type == "fill_blank_type":
            return build_fill_blank_type_item(word, user_word_id)
        elif review_type == "odd_one_out":
            return self._build_odd_one_out(word, user_word_id, pool)
        elif review_type == "true_false":
            return build_true_false_item(word, user_word_id, pool)
        elif review_type == "word_in_context":
            return build_word_in_context_item(word, user_word_id, pool)
        else:
            return build_mcq_item(word, user_word_id, pool)

    def _build_odd_one_out(
        self,
        word: WordCard,
        user_word_id: int,
        pool: list[WordCard],
    ) -> ReviewItem:
        synonyms = word.synonyms[:2]
        synonym_set = set(s.lower() for s in word.synonyms)
        synonym_set.add(word.word.lower())
        odd_candidates = [
            w.word
            for w in pool
            if w.id != word.id and w.word.lower() not in synonym_set
        ]
        if odd_candidates:
            odd_word = random.choice(odd_candidates)
        else:
            odd_word = random.choice([w.word for w in pool if w.id != word.id])
        return build_odd_one_out_item(word, user_word_id, synonyms, odd_word)

    async def submit_review(
        self,
        user_id: int,
        user_word_id: int,
        review_type: str,
        was_correct: bool,
        response_time_ms: int | None = None,
        typed_answer: str | None = None,
    ) -> ReviewResult:
        user_word = await self.user_word_repo.get_by_id(user_word_id)
        if not user_word or user_word.user_id != user_id:
            raise ValueError("Word not found")

        rating = 3 if was_correct else 1

        fsrs_card_json = user_word.fsrs_card_json
        if not fsrs_card_json:
            from app.utils.fsrs_helper import create_new_card

            fsrs_card_json = create_new_card()

        updated_card, log_json, next_due = review_card(fsrs_card_json, rating)

        await self.user_word_repo.update(
            user_word,
            fsrs_card_json=updated_card,
            due_at=next_due,
            last_reviewed_at=datetime.now(timezone.utc),
            reps=user_word.reps + 1,
            lapses=user_word.lapses + (1 if rating == 1 else 0),
            status="reviewing",
        )

        await self.review_log_repo.create(
            user_id=user_id,
            user_word_id=user_word_id,
            rating=rating,
            review_type=review_type,
            fsrs_log_json=log_json,
            was_correct=was_correct,
            response_time_ms=response_time_ms,
        )

        return ReviewResult(
            user_word_id=user_word_id,
            next_due=next_due,
            was_correct=was_correct,
            rating=rating,
        )

    async def submit_review_batch(
        self,
        user_id: int,
        review_type: str,
        results: list[dict],
        total_time_ms: int | None = None,
    ) -> list[ReviewResult]:
        review_results = []
        per_word_time = (
            (total_time_ms // len(results))
            if total_time_ms and results
            else None
        )
        for r in results:
            result = await self.submit_review(
                user_id=user_id,
                user_word_id=r["user_word_id"],
                review_type=review_type,
                was_correct=r["was_correct"],
                response_time_ms=per_word_time,
            )
            review_results.append(result)
        return review_results
