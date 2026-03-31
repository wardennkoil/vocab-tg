import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

    async def _call(self, method: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}/{method}"
        response = await self.client.post(url, json=kwargs)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram API error: {data.get('description', 'unknown')}")
        return data.get("result", {})

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: dict | None = None,
    ) -> dict:
        kwargs: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup:
            kwargs["reply_markup"] = reply_markup
        return await self._call("sendMessage", **kwargs)

    async def set_webhook(self, url: str) -> dict:
        return await self._call("setWebhook", url=url)

    async def set_my_commands(self, commands: list[dict]) -> dict:
        return await self._call("setMyCommands", commands=commands)

    async def set_chat_menu_button(self, menu_button: dict) -> dict:
        return await self._call("setChatMenuButton", menu_button=menu_button)
