import datetime as dt

from sqlalchemy import BigInteger, Boolean, Date, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    language_code: Mapped[str] = mapped_column(String(10), server_default="en")
    timezone: Mapped[str] = mapped_column(
        String(50), server_default="America/New_York"
    )
    daily_push_hour: Mapped[int] = mapped_column(SmallInteger, server_default="9")
    daily_word_count: Mapped[int] = mapped_column(SmallInteger, server_default="5")
    difficulty_level: Mapped[str] = mapped_column(
        String(10), server_default="B2-C1"
    )
    skip_triage: Mapped[bool] = mapped_column(Boolean, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    last_push_sent_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)

    user_words: Mapped[list["UserWord"]] = relationship(back_populates="user")
    review_logs: Mapped[list["ReviewLog"]] = relationship(back_populates="user")
    daily_sessions: Mapped[list["DailySession"]] = relationship(back_populates="user")
