from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_review_service, get_user_service
from app.schemas.review import (
    ReviewBatchResult,
    ReviewBatchSubmit,
    ReviewResult,
    ReviewSession,
    ReviewSubmit,
)
from app.services.review_service import ReviewService
from app.services.user_service import UserService

router = APIRouter(prefix="/users/{telegram_id}/reviews", tags=["reviews"])


@router.get("/due")
async def get_due(
    telegram_id: int,
    user_service: UserService = Depends(get_user_service),
    review_service: ReviewService = Depends(get_review_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    count = await review_service.get_due_count(user.id)
    return {"due_count": count}


@router.post("/session", response_model=ReviewSession)
async def create_session(
    telegram_id: int,
    exclude_types: str | None = Query(
        None, description="Comma-separated review types to exclude"
    ),
    user_service: UserService = Depends(get_user_service),
    review_service: ReviewService = Depends(get_review_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    excluded = (
        [t.strip() for t in exclude_types.split(",")]
        if exclude_types
        else None
    )
    return await review_service.create_review_session(
        user, exclude_types=excluded
    )


@router.post("/submit", response_model=ReviewResult)
async def submit_review(
    telegram_id: int,
    data: ReviewSubmit,
    user_service: UserService = Depends(get_user_service),
    review_service: ReviewService = Depends(get_review_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return await review_service.submit_review(
            user_id=user.id,
            user_word_id=data.user_word_id,
            review_type=data.review_type,
            was_correct=data.was_correct,
            response_time_ms=data.response_time_ms,
            typed_answer=data.typed_answer,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/submit-batch", response_model=ReviewBatchResult)
async def submit_review_batch(
    telegram_id: int,
    data: ReviewBatchSubmit,
    user_service: UserService = Depends(get_user_service),
    review_service: ReviewService = Depends(get_review_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        results = await review_service.submit_review_batch(
            user_id=user.id,
            review_type=data.review_type,
            results=[r.model_dump() for r in data.results],
            total_time_ms=data.total_time_ms,
        )
        return ReviewBatchResult(results=results)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
