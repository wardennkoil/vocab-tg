from pydantic import BaseModel


class StatsOverview(BaseModel):
    total_words: int
    words_learning: int
    words_known: int
    current_streak: int
    accuracy_rate: float | None
    reviews_today: int
    due_tomorrow: int


class DayStats(BaseModel):
    date: str
    review_count: int


class StatsHistory(BaseModel):
    days: list[DayStats]
