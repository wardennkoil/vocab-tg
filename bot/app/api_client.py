import logging

import httpx

logger = logging.getLogger(__name__)


class VocabAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api/v1",
            timeout=httpx.Timeout(15.0, connect=5.0),
        )

    async def close(self):
        await self.client.aclose()

    async def register_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        language_code: str | None = None,
    ) -> dict:
        response = await self.client.post(
            "/users/register",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "language_code": language_code,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_pending_notifications(self) -> list[dict]:
        response = await self.client.get("/notifications/pending")
        response.raise_for_status()
        return response.json()

    async def mark_notifications_sent(self, user_ids: list[int]) -> dict:
        response = await self.client.post(
            "/notifications/mark-sent",
            json={"user_ids": user_ids},
        )
        response.raise_for_status()
        return response.json()
