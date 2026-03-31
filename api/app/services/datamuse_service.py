import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.datamuse.com"


@dataclass
class WordSuggestion:
    word: str
    score: int = 0


class DatamuseService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def suggest(self, prefix: str, max_results: int = 10) -> list[WordSuggestion]:
        try:
            response = await self.http_client.get(
                f"{BASE_URL}/sug",
                params={"s": prefix, "max": max_results},
                timeout=5.0,
            )
            response.raise_for_status()
            return [
                WordSuggestion(word=item["word"], score=item.get("score", 0))
                for item in response.json()
            ]
        except httpx.HTTPError as e:
            logger.error(f"Datamuse suggest error for '{prefix}': {e}")
            return []

    async def get_synonyms(self, word: str, max_results: int = 10) -> list[str]:
        try:
            response = await self.http_client.get(
                f"{BASE_URL}/words",
                params={"rel_syn": word, "max": max_results},
                timeout=5.0,
            )
            response.raise_for_status()
            return [item["word"] for item in response.json()]
        except httpx.HTTPError as e:
            logger.error(f"Datamuse synonyms error for '{word}': {e}")
            return []

    async def search_words(self, pattern: str, max_results: int = 10) -> list[WordSuggestion]:
        try:
            response = await self.http_client.get(
                f"{BASE_URL}/words",
                params={"sp": pattern, "md": "df", "max": max_results},
                timeout=5.0,
            )
            response.raise_for_status()
            return [
                WordSuggestion(word=item["word"], score=item.get("score", 0))
                for item in response.json()
            ]
        except httpx.HTTPError as e:
            logger.error(f"Datamuse search error for '{pattern}': {e}")
            return []
