"""Validate word pool entries and remove invalid words.

Two-pass approach:
  1. Local check against Simple English Wiktionary (simple-extract.jsonl)
  2. API check against Free Dictionary API for words not in Wiktionary

Usage:
    UV_CACHE_DIR=/tmp/uv-cache uv run python -m scripts.cleanup_word_pool
    UV_CACHE_DIR=/tmp/uv-cache uv run python -m scripts.cleanup_word_pool --dry-run
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import async_session_factory
from app.models.user_word import UserWord
from app.models.word_pool import WordPool

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"
REQUEST_DELAY = 1.0
BATCH_SIZE = 50
WIKTIONARY_FILE = Path(__file__).parent.parent.parent / "simple-extract.jsonl"


def load_wiktionary_words() -> set[str]:
    """Load unique lowercase words from Simple English Wiktionary JSONL."""
    words = set()
    with open(WIKTIONARY_FILE) as f:
        for line in f:
            obj = json.loads(line)
            w = obj.get("word")
            if w:
                words.add(w.lower())
    logger.info(f"Loaded {len(words)} unique words from Wiktionary")
    return words


async def check_word_exists(http_client: httpx.AsyncClient, word: str) -> bool | None:
    """Check if a word exists in Free Dictionary API.

    Returns True (exists), False (confirmed 404), or None (error/uncertain).
    """
    backoff = [5, 15, 30, 60]
    for attempt in range(len(backoff) + 1):
        try:
            response = await http_client.get(
                f"{DICTIONARY_API_URL}/{word.lower().strip()}", timeout=5.0
            )
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                return False
            if response.status_code == 429:
                if attempt < len(backoff):
                    wait = backoff[attempt]
                    logger.warning(f"Rate limited, waiting {wait}s (attempt {attempt + 1})...")
                    await asyncio.sleep(wait)
                    continue
                logger.error("Rate limit retries exhausted")
                return None
            logger.warning(f"Unexpected status {response.status_code} for '{word}'")
            return None
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error for '{word}': {e}")
            return None
    return None


async def delete_pool_entry(db: AsyncSession, entry: WordPool) -> None:
    """Delete a WordPool entry and its Word if orphaned."""
    word_id = entry.word_id
    word_obj = entry.word

    await db.delete(entry)

    # Check if the Word row is now orphaned
    other_pool = await db.execute(
        select(WordPool.id).where(
            WordPool.word_id == word_id,
            WordPool.id != entry.id,
        )
    )
    has_users = await db.execute(
        select(UserWord.id).where(UserWord.word_id == word_id).limit(1)
    )
    if not other_pool.scalar_one_or_none() and not has_users.scalar_one_or_none():
        await db.delete(word_obj)


async def cleanup_word_pool(
    db: AsyncSession, http_client: httpx.AsyncClient, *, dry_run: bool = False
) -> None:
    wiktionary_words = load_wiktionary_words()

    result = await db.execute(
        select(WordPool).options(joinedload(WordPool.word)).order_by(WordPool.source_rank)
    )
    pool_entries = list(result.scalars().unique().all())

    total = len(pool_entries)
    logger.info(f"Checking {total} word pool entries...")
    if dry_run:
        logger.info("DRY RUN — no deletions will be performed")

    # Pass 1: local Wiktionary check
    needs_api_check = []
    skipped_enriched = 0
    skipped_wiktionary = 0

    for entry in pool_entries:
        word_text = entry.word.word.lower()

        if entry.word.is_enriched:
            skipped_enriched += 1
            continue

        if word_text in wiktionary_words:
            skipped_wiktionary += 1
            continue

        needs_api_check.append(entry)

    logger.info(
        f"Pass 1 done: {skipped_enriched} enriched, {skipped_wiktionary} in Wiktionary, "
        f"{len(needs_api_check)} need API check"
    )

    # Pass 2: API check for remaining words
    removed = 0
    kept = 0
    errors = 0

    for i, entry in enumerate(needs_api_check, 1):
        word_text = entry.word.word

        if i % 50 == 0:
            logger.info(
                f"API progress: {i}/{len(needs_api_check)} checked, "
                f"{removed} removed, {kept} kept, {errors} errors"
            )

        exists = await check_word_exists(http_client, word_text)

        if exists is True:
            kept += 1
        elif exists is False:
            logger.info(
                f"{'[DRY RUN] Would remove' if dry_run else 'Removing'} "
                f"'{word_text}' (rank={entry.source_rank})"
            )
            removed += 1
            if not dry_run:
                await delete_pool_entry(db, entry)
        else:
            errors += 1

        await asyncio.sleep(REQUEST_DELAY)

        if not dry_run and i % BATCH_SIZE == 0:
            await db.commit()

    if not dry_run:
        await db.commit()

    logger.info(
        f"Done! total={total}, skipped_enriched={skipped_enriched}, "
        f"skipped_wiktionary={skipped_wiktionary}, api_checked={len(needs_api_check)}, "
        f"removed={removed}, kept={kept}, errors={errors}"
    )


async def main() -> None:
    dry_run = "--dry-run" in sys.argv

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
    ) as http_client:
        async with async_session_factory() as db:
            await cleanup_word_pool(db, http_client, dry_run=dry_run)


if __name__ == "__main__":
    asyncio.run(main())
