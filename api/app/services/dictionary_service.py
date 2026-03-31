import logging
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"


@dataclass
class WordDefinition:
    word: str
    phonetic: str | None = None
    audio_url: str | None = None
    definition: str | None = None
    definitions: list[dict] = field(default_factory=list)
    example: str | None = None
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)
    part_of_speech: str | None = None


class DictionaryService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def lookup(self, word: str) -> WordDefinition | None:
        try:
            response = await self.http_client.get(
                f"{BASE_URL}/{word.lower().strip()}", timeout=5.0
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return self._parse_response(word, data)
        except httpx.HTTPError as e:
            logger.error(f"Dictionary API error for '{word}': {e}")
            return None

    def _parse_response(self, word: str, data: list[dict]) -> WordDefinition:
        if not data:
            return WordDefinition(word=word)

        entry = data[0]
        phonetic = None
        audio_url = None
        for p in entry.get("phonetics", []):
            if p.get("text") and not phonetic:
                phonetic = p["text"]
            if p.get("audio") and not audio_url:
                audio_url = p["audio"]

        definition = None
        example = None
        part_of_speech = None
        synonyms = set()
        antonyms = set()
        definitions = []

        for meaning in entry.get("meanings", []):
            pos = meaning.get("partOfSpeech", "")
            if not part_of_speech:
                part_of_speech = pos

            for syn in meaning.get("synonyms", []):
                synonyms.add(syn)
            for ant in meaning.get("antonyms", []):
                antonyms.add(ant)

            for defn in meaning.get("definitions", []):
                definitions.append({
                    "part_of_speech": pos,
                    "definition": defn.get("definition", ""),
                    "example": defn.get("example"),
                })
                if not definition:
                    definition = defn.get("definition")
                if not example and defn.get("example"):
                    example = defn["example"]
                for syn in defn.get("synonyms", []):
                    synonyms.add(syn)
                for ant in defn.get("antonyms", []):
                    antonyms.add(ant)

        return WordDefinition(
            word=entry.get("word", word),
            phonetic=phonetic,
            audio_url=audio_url,
            definition=definition,
            definitions=definitions,
            example=example,
            synonyms=list(synonyms)[:20],
            antonyms=list(antonyms)[:20],
            part_of_speech=part_of_speech,
        )
