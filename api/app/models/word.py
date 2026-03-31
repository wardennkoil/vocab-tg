from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class Word(Base, IDMixin, TimestampMixin):
    __tablename__ = "words"

    word: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    phonetic: Mapped[str | None] = mapped_column(String(200))
    audio_url: Mapped[str | None] = mapped_column(String(500))
    definition: Mapped[str | None] = mapped_column(Text)
    definitions_json: Mapped[dict | None] = mapped_column(JSONB)
    translation_ru: Mapped[str | None] = mapped_column(String(500))
    example_sentence: Mapped[str | None] = mapped_column(Text)
    synonyms: Mapped[list] = mapped_column(JSONB, server_default="[]")
    antonyms: Mapped[list] = mapped_column(JSONB, server_default="[]")
    topics: Mapped[list] = mapped_column(JSONB, server_default="[]")
    part_of_speech: Mapped[str | None] = mapped_column(String(50))
    frequency_rank: Mapped[int | None] = mapped_column(Integer, index=True)
    difficulty_band: Mapped[str | None] = mapped_column(String(10), index=True)
    is_enriched: Mapped[bool] = mapped_column(Boolean, server_default="false")
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    word_pool_entries: Mapped[list["WordPool"]] = relationship(back_populates="word")
    user_words: Mapped[list["UserWord"]] = relationship(back_populates="word")
