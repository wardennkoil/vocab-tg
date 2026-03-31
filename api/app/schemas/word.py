from datetime import datetime

from pydantic import BaseModel


class WordCard(BaseModel):
    id: int
    word: str
    phonetic: str | None = None
    audio_url: str | None = None
    definition: str | None = None
    definitions_json: list[dict] | None = None
    translation_ru: str | None = None
    example_sentence: str | None = None
    synonyms: list[str] = []
    antonyms: list[str] = []
    part_of_speech: str | None = None
    difficulty_band: str | None = None

    model_config = {"from_attributes": True}


class WordSuggestion(BaseModel):
    word: str
    score: int = 0


class AddWordRequest(BaseModel):
    word: str


class UserWordResponse(BaseModel):
    id: int
    user_id: int
    word_id: int
    status: str
    source: str
    due_at: datetime | None = None
    reps: int
    lapses: int
    added_at: datetime
    last_reviewed_at: datetime | None = None
    word: WordCard

    model_config = {"from_attributes": True}


class PaginatedUserWords(BaseModel):
    items: list[UserWordResponse]
    total: int
    page: int
    per_page: int
