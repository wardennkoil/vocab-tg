from pydantic import BaseModel

from app.schemas.word import WordCard


class TriageCandidate(BaseModel):
    word_id: int
    word: str
    definition: str | None = None


class TriageCandidatesResponse(BaseModel):
    candidates: list[TriageCandidate]
    session_id: int


class TriageSubmit(BaseModel):
    session_id: int
    known_word_ids: list[int]
    unknown_word_ids: list[int]


class DailyWordsResponse(BaseModel):
    words: list[WordCard]
    session_date: str
    status: str
