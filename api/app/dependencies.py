from collections.abc import AsyncGenerator

import httpx
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory
from app.services.daily_service import DailyService
from app.services.notification_service import NotificationService
from app.services.review_service import ReviewService
from app.services.stats_service import StatsService
from app.services.translation_service import TranslationService
from app.services.user_service import UserService
from app.services.word_service import WordService

_http_client: httpx.AsyncClient | None = None
_translation_service: TranslationService | None = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


def get_translation_service() -> TranslationService:
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService(
            deepl_api_key=settings.DEEPL_API_KEY or None
        )
    return _translation_service


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_word_service(
    db: AsyncSession = Depends(get_db),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    translation_service: TranslationService = Depends(get_translation_service),
) -> WordService:
    return WordService(db, http_client, translation_service)


def get_daily_service(
    db: AsyncSession = Depends(get_db),
    word_service: WordService = Depends(get_word_service),
) -> DailyService:
    return DailyService(db, word_service)


def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    return ReviewService(db)


def get_stats_service(db: AsyncSession = Depends(get_db)) -> StatsService:
    return StatsService(db)


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


async def verify_cron_secret(authorization: str = Header(...)) -> None:
    if not settings.CRON_SECRET:
        raise HTTPException(status_code=503, detail="CRON_SECRET not configured")
    if authorization != f"Bearer {settings.CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Invalid authorization")
