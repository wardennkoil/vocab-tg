from datetime import datetime

from pydantic import BaseModel

from app.schemas.word import WordCard


# --- Type-specific data models ---


class MCQData(BaseModel):
    options: list[WordCard]
    correct_index: int


class ReverseMCQData(BaseModel):
    definition_options: list[str]
    correct_index: int


class FillBlankMCQData(BaseModel):
    sentence_with_blank: str
    options: list[str]
    correct_index: int


class FillBlankTypeData(BaseModel):
    sentence_with_blank: str
    correct_answer: str
    accept_alternatives: list[str] = []


class MatchingPair(BaseModel):
    user_word_id: int
    word: str
    definition: str


class MatchingData(BaseModel):
    pairs: list[MatchingPair]


class OddOneOutData(BaseModel):
    words: list[str]
    odd_index: int


class TrueFalseData(BaseModel):
    shown_definition: str
    is_correct_pair: bool


class WordInContextData(BaseModel):
    sentence: str
    definition_options: list[str]
    correct_index: int


# --- ReviewItem (polymorphic on type, one *_data field populated) ---


class ReviewItem(BaseModel):
    type: str
    user_word_id: int | None = None
    word: WordCard | None = None
    mcq_data: MCQData | None = None
    reverse_mcq_data: ReverseMCQData | None = None
    fill_blank_mcq_data: FillBlankMCQData | None = None
    fill_blank_type_data: FillBlankTypeData | None = None
    matching_data: MatchingData | None = None
    odd_one_out_data: OddOneOutData | None = None
    true_false_data: TrueFalseData | None = None
    word_in_context_data: WordInContextData | None = None


class ReviewSession(BaseModel):
    items: list[ReviewItem]
    total: int
    due_count: int


# --- Submission ---


class ReviewSubmit(BaseModel):
    user_word_id: int
    review_type: str
    was_correct: bool
    response_time_ms: int | None = None
    typed_answer: str | None = None


class ReviewBatchSubmit(BaseModel):
    review_type: str = "matching"
    results: list[ReviewSubmit]
    total_time_ms: int | None = None


class ReviewResult(BaseModel):
    user_word_id: int
    next_due: datetime | None
    was_correct: bool | None = None
    rating: int


class ReviewBatchResult(BaseModel):
    results: list[ReviewResult]
