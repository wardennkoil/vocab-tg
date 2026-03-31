from datetime import date, datetime

from pydantic import BaseModel


class UserRegister(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    language_code: str | None = None


class UserSettingsUpdate(BaseModel):
    timezone: str | None = None
    daily_push_hour: int | None = None
    daily_word_count: int | None = None
    difficulty_level: str | None = None
    skip_triage: bool | None = None


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    timezone: str
    daily_push_hour: int
    daily_word_count: int
    difficulty_level: str
    skip_triage: bool
    is_active: bool
    last_push_sent_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}
