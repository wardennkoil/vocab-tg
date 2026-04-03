import logging

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.config import settings
from app.dependencies import (
    get_http_client,
    get_notification_service,
    verify_cron_secret,
)
from app.services.notification_service import NotificationService
from app.services.telegram_bot_service import TelegramBotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class PendingNotification(BaseModel):
    telegram_id: int
    user_id: int
    first_name: str | None
    due_count: int
    has_daily_session: bool


class MarkSentRequest(BaseModel):
    user_ids: list[int]


class MarkSentResponse(BaseModel):
    marked_count: int


class TriggerResponse(BaseModel):
    notified_count: int
    errors: int


@router.get("/pending", response_model=list[PendingNotification])
async def get_pending(
    service: NotificationService = Depends(get_notification_service),
):
    return await service.get_pending_notifications()


@router.post("/mark-sent", response_model=MarkSentResponse)
async def mark_sent(
    data: MarkSentRequest,
    service: NotificationService = Depends(get_notification_service),
):
    count = await service.mark_sent(data.user_ids)
    return MarkSentResponse(marked_count=count)


@router.post(
    "/trigger",
    dependencies=[Depends(verify_cron_secret)],
)
async def trigger_notifications(
    service: NotificationService = Depends(get_notification_service),
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> PlainTextResponse:
    pending = await service.get_pending_notifications()
    if not pending:
        return PlainTextResponse("OK")

    tg = TelegramBotService(http_client)
    sent_user_ids = []
    error_count = 0

    for entry in pending:
        text = _build_notification_text(
            entry.get("first_name") or "there",
            entry.get("due_count", 0),
            entry.get("has_daily_session", False),
        )
        reply_markup = _build_notification_keyboard(
            entry.get("due_count", 0),
            entry.get("has_daily_session", False),
        )

        try:
            await tg.send_message(
                chat_id=entry["telegram_id"],
                text=text,
                reply_markup=reply_markup,
            )
            sent_user_ids.append(entry["user_id"])
        except Exception:
            logger.warning(
                "Failed to notify telegram_id=%d", entry["telegram_id"], exc_info=True
            )
            error_count += 1

    if sent_user_ids:
        await service.mark_sent(sent_user_ids)

    if error_count > 0:
        return PlainTextResponse("ERROR", status_code=207)

    return PlainTextResponse("OK")


def _build_notification_text(
    first_name: str, due_count: int, has_daily: bool
) -> str:
    lines = [f"Hi {first_name}!"]
    if not has_daily:
        lines.append("Your daily words are ready to learn!")
    if due_count > 0:
        lines.append(f"You have {due_count} words due for review.")
    elif has_daily:
        lines.append("Great job staying on track!")
    lines.append("\nTap a button below to get started.")
    return "\n".join(lines)


def _build_notification_keyboard(due_count: int, has_daily: bool) -> dict:
    buttons = []
    if not has_daily:
        buttons.append([{
            "text": "Learn New Words",
            "web_app": {"url": f"{settings.MINI_APP_URL}/daily"},
        }])
    if due_count > 0:
        buttons.append([{
            "text": f"Review Words ({due_count})",
            "web_app": {"url": f"{settings.MINI_APP_URL}/review"},
        }])
    if not buttons:
        buttons.append([{
            "text": "Open App",
            "web_app": {"url": settings.MINI_APP_URL},
        }])
    return {"inline_keyboard": buttons}
