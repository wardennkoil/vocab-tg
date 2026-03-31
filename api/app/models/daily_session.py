import datetime as dt

from sqlalchemy import BigInteger, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class DailySession(Base, IDMixin, TimestampMixin):
    __tablename__ = "daily_sessions"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "session_date", name="uq_daily_sessions_user_date"
        ),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    session_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    triage_word_ids: Mapped[list] = mapped_column(JSONB, server_default="[]")
    selected_word_ids: Mapped[list] = mapped_column(JSONB, server_default="[]")
    known_word_ids: Mapped[list] = mapped_column(JSONB, server_default="[]")
    daily_word_ids: Mapped[list] = mapped_column(JSONB, server_default="[]")
    status: Mapped[str] = mapped_column(
        String(20), server_default="pending", nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="daily_sessions")
