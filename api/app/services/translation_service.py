import logging

import deepl
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self, deepl_api_key: str | None = None):
        self.deepl_client: deepl.DeepLClient | None = None
        if deepl_api_key:
            try:
                self.deepl_client = deepl.DeepLClient(auth_key=deepl_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize DeepL client: {e}")

        self.google_translator = GoogleTranslator(source="en", target="ru")

    async def translate_to_russian(self, text: str) -> str | None:
        result = await self._deepl_translate(text)
        if result:
            return result
        return self._google_translate_fallback(text)

    async def _deepl_translate(self, text: str) -> str | None:
        if not self.deepl_client:
            return None
        try:
            result = self.deepl_client.translate_text(text, target_lang="RU")
            return result.text
        except Exception as e:
            logger.warning(f"DeepL translation failed for '{text}': {e}")
            return None

    def _google_translate_fallback(self, text: str) -> str | None:
        try:
            return self.google_translator.translate(text)
        except Exception as e:
            logger.warning(f"Google Translate fallback failed for '{text}': {e}")
            return None
