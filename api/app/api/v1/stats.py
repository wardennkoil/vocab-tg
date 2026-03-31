from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_stats_service, get_user_service
from app.schemas.stats import StatsHistory, StatsOverview
from app.services.stats_service import StatsService
from app.services.user_service import UserService

router = APIRouter(prefix="/users/{telegram_id}/stats", tags=["stats"])


@router.get("", response_model=StatsOverview)
async def get_stats(
    telegram_id: int,
    user_service: UserService = Depends(get_user_service),
    stats_service: StatsService = Depends(get_stats_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await stats_service.get_overview(user.id)


@router.get("/history", response_model=StatsHistory)
async def get_history(
    telegram_id: int,
    days: int = 30,
    user_service: UserService = Depends(get_user_service),
    stats_service: StatsService = Depends(get_stats_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await stats_service.get_history(user.id, days)
