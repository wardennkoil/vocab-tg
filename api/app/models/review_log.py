from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Index, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin


class ReviewLog(Base, IDMixin):
    __tablename__ = "review_logs"
    __table_args__ = (
        Index("ix_review_logs_user_reviewed", "user_id", "reviewed_at"),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    user_word_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user_words.id"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    review_type: Mapped[str] = mapped_column(String(20), nullable=False)
    fsrs_log_json: Mapped[dict | None] = mapped_column(JSONB)
    scheduled_days: Mapped[float | None] = mapped_column(Float)
    elapsed_days: Mapped[float | None] = mapped_column(Float)
    was_correct: Mapped[bool | None] = mapped_column(Boolean)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="review_logs")
    user_word: Mapped["UserWord"] = relationship(back_populates="review_logs")
