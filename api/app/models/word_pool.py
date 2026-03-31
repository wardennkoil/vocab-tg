from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class WordPool(Base, IDMixin, TimestampMixin):
    __tablename__ = "word_pool"
    __table_args__ = (
        UniqueConstraint("word_id", "source", name="uq_word_pool_word_source"),
    )

    word_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("words.id"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_rank: Mapped[int | None] = mapped_column(Integer)

    word: Mapped["Word"] = relationship(back_populates="word_pool_entries")
