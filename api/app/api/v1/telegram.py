import logging

import httpx
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.config import settings
from app.dependencies import get_http_client, get_user_service, verify_cron_secret
from app.services.telegram_bot_service import TelegramBotService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["telegram"])


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    body = await request.json()
    message = body.get("message")
    if not message:
        return {"ok": True}

    text = message.get("text", "")
    from_user = message.get("from", {})
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": True}

    if text.startswith("/start"):
        telegram_id = from_user.get("id")
        username = from_user.get("username")
        first_name = from_user.get("first_name")
        language_code = from_user.get("language_code")

        await user_service.get_or_create_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language_code=language_code,
        )

        tg = TelegramBotService(http_client)
        await tg.send_message(
            chat_id=chat_id,
            text=(
                f"Welcome, {first_name or 'there'}!\n\n"
                "I'm your vocabulary learning assistant. "
                "Tap the button below to open the app and start learning!\n\n"
                "I'll also send you daily reminders when it's time to learn or review."
            ),
            reply_markup={
                "inline_keyboard": [[{
                    "text": "Open Vocab App",
                    "web_app": {"url": settings.MINI_APP_URL},
                }]]
            },
        )

    return {"ok": True}


class SetupRequest(BaseModel):
    api_base_url: str


class SetupResponse(BaseModel):
    webhook: str
    commands: str
    menu_button: str


@router.post(
    "/setup",
    response_model=SetupResponse,
    dependencies=[Depends(verify_cron_secret)],
)
async def setup_webhook(
    data: SetupRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    tg = TelegramBotService(http_client)

    webhook_url = f"{data.api_base_url.rstrip('/')}/api/v1/webhook/telegram"
    await tg.set_webhook(webhook_url)

    await tg.set_my_commands([
        {"command": "start", "description": "Start the bot"},
    ])

    await tg.set_chat_menu_button({
        "type": "web_app",
        "text": "Open App",
        "web_app": {"url": settings.MINI_APP_URL},
    })

    return SetupResponse(
        webhook=f"Set webhook to {webhook_url}",
        commands="Registered /start command",
        menu_button=f"Set menu button to {settings.MINI_APP_URL}",
    )
