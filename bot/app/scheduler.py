import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, ContextTypes

from app.api_client import VocabAPIClient
from app.config import settings

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 15 * 60


def schedule_notification_check(application: Application) -> None:
    application.job_queue.run_repeating(
        callback=check_and_send_notifications,
        interval=CHECK_INTERVAL_SECONDS,
        first=10,
        name="notification_check",
    )
    logger.info(
        "Notification check scheduled every %d minutes.",
        CHECK_INTERVAL_SECONDS // 60,
    )


async def check_and_send_notifications(context: ContextTypes.DEFAULT_TYPE) -> None:
    api: VocabAPIClient = context.bot_data["api_client"]

    try:
        pending = await api.get_pending_notifications()
    except Exception:
        logger.exception("Failed to fetch pending notifications")
        return

    if not pending:
        return

    logger.info("Sending notifications to %d users.", len(pending))

    sent_user_ids = []
    for entry in pending:
        telegram_id = entry["telegram_id"]
        first_name = entry.get("first_name") or "there"
        due_count = entry.get("due_count", 0)
        has_daily = entry.get("has_daily_session", False)

        text = _build_notification_text(first_name, due_count, has_daily)
        keyboard = _build_notification_keyboard(due_count, has_daily)

        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=keyboard,
            )
            sent_user_ids.append(entry["user_id"])
        except Exception:
            logger.warning("Failed to send notification to %d", telegram_id, exc_info=True)

    if sent_user_ids:
        try:
            await api.mark_notifications_sent(sent_user_ids)
            logger.info("Marked %d users as notified.", len(sent_user_ids))
        except Exception:
            logger.exception("Failed to mark notifications as sent")


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


def _build_notification_keyboard(
    due_count: int, has_daily: bool
) -> InlineKeyboardMarkup:
    buttons = []

    if not has_daily:
        buttons.append([InlineKeyboardButton(
            "Learn New Words",
            web_app=WebAppInfo(url=f"{settings.MINI_APP_URL}/daily"),
        )])

    if due_count > 0:
        buttons.append([InlineKeyboardButton(
            f"Review Words ({due_count})",
            web_app=WebAppInfo(url=f"{settings.MINI_APP_URL}/review"),
        )])

    if not buttons:
        buttons.append([InlineKeyboardButton(
            "Open App",
            web_app=WebAppInfo(url=settings.MINI_APP_URL),
        )])

    return InlineKeyboardMarkup(buttons)
