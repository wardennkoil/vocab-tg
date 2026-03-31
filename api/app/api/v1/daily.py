from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_daily_service, get_user_service
from app.schemas.daily import DailyWordsResponse, TriageCandidatesResponse, TriageSubmit
from app.schemas.word import WordCard
from app.services.daily_service import DailyService
from app.services.user_service import UserService

router = APIRouter(prefix="/users/{telegram_id}/daily", tags=["daily"])


@router.post("/triage", response_model=TriageCandidatesResponse)
async def generate_triage(
    telegram_id: int,
    user_service: UserService = Depends(get_user_service),
    daily_service: DailyService = Depends(get_daily_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await daily_service.generate_triage_candidates(user)


@router.post("/triage/submit", response_model=list[WordCard])
async def submit_triage(
    telegram_id: int,
    data: TriageSubmit,
    user_service: UserService = Depends(get_user_service),
    daily_service: DailyService = Depends(get_daily_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await daily_service.submit_triage(
        user, data.session_id, data.known_word_ids, data.unknown_word_ids
    )


@router.post("/auto-select", response_model=list[WordCard])
async def auto_select(
    telegram_id: int,
    user_service: UserService = Depends(get_user_service),
    daily_service: DailyService = Depends(get_daily_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await daily_service.auto_select_daily(user)


@router.get("/today", response_model=DailyWordsResponse)
async def get_today(
    telegram_id: int,
    user_service: UserService = Depends(get_user_service),
    daily_service: DailyService = Depends(get_daily_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await daily_service.get_today_words(user)
