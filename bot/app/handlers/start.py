from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CommandHandler, ContextTypes

from app.api_client import VocabAPIClient
from app.config import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api: VocabAPIClient = context.bot_data["api_client"]
    user = update.effective_user

    await api.register_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language_code=user.language_code,
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Open Vocab App",
            web_app=WebAppInfo(url=settings.MINI_APP_URL),
        )]
    ])

    await update.message.reply_text(
        f"Welcome, {user.first_name or 'there'}!\n\n"
        "I'm your vocabulary learning assistant. "
        "Tap the button below to open the app and start learning!\n\n"
        "I'll also send you daily reminders when it's time to learn or review.",
        reply_markup=keyboard,
    )


handler = CommandHandler("start", start_command)
