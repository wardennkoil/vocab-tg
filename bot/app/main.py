import logging

from telegram import BotCommand, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application

from app.api_client import VocabAPIClient
from app.config import settings
from app.handlers import start
from app.scheduler import schedule_notification_check

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
    ])

    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Open App",
            web_app=WebAppInfo(url=settings.MINI_APP_URL),
        )
    )

    schedule_notification_check(application)

    logger.info("Bot initialized with Mini App menu and notification scheduler.")


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return

    api_client = VocabAPIClient(settings.API_BASE_URL)

    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.bot_data["api_client"] = api_client

    application.add_handler(start.handler)

    logger.info("Bot starting (API: %s)...", settings.API_BASE_URL)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
