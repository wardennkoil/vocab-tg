from fastapi import APIRouter

from app.api.v1.daily import router as daily_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.stats import router as stats_router
from app.api.v1.telegram import router as telegram_router
from app.api.v1.users import router as users_router
from app.api.v1.words import router as words_router

router = APIRouter()
router.include_router(users_router)
router.include_router(words_router)
router.include_router(daily_router)
router.include_router(reviews_router)
router.include_router(stats_router)
router.include_router(notifications_router)
router.include_router(telegram_router)
