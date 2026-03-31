"""Seed the word pool from Wiktionary data, AI classifications, and frequency list.

Data sources:
  1. simple-extract.jsonl — Wiktionary definitions, phonetics, examples, synonyms
  2. wiktionary_classified.jsonl — AI-generated CEFR levels and topic tags
  3. frequency_list.txt — Google 10K frequency ranks

Run: UV_CACHE_DIR=/tmp/uv-cache uv run python -m scripts.seed_word_pool
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.word import Word
from app.models.word_pool import WordPool
from app.utils.difficulty import cefr_to_difficulty_band

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
WIKTIONARY_FILE = DATA_DIR / "simple-extract.jsonl"
CLASSIFIED_FILE = DATA_DIR / "wiktionary_classified.jsonl"
FREQUENCY_FILE = DATA_DIR / "frequency_list.txt"

WIKTIONARY_AUDIO_BASE = "https://upload.wikimedia.org/wikipedia/commons"
COMMIT_BATCH_SIZE = 500


def load_frequency_ranks() -> dict[str, int]:
    """Load word → frequency rank mapping from Google 10K list."""
    ranks = {}
    if not FREQUENCY_FILE.exists():
        logger.warning(f"Frequency list not found: {FREQUENCY_FILE}")
        return ranks
    for rank, line in enumerate(FREQUENCY_FILE.read_text().strip().split("\n"), start=1):
        word = line.strip().lower()
        if word and word not in ranks:
            ranks[word] = rank
    logger.info(f"Loaded {len(ranks)} frequency ranks")
    return ranks


def load_classifications() -> dict[str, dict]:
    """Load word → {cefr, topics} from AI classification output."""
    classifications = {}
    if not CLASSIFIED_FILE.exists():
        logger.warning(f"Classification file not found: {CLASSIFIED_FILE}")
        return classifications
    with open(CLASSIFIED_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                classifications[obj["word"].lower()] = obj
            except (json.JSONDecodeError, KeyError):
                continue
    logger.info(f"Loaded {len(classifications)} word classifications")
    return classifications


def parse_wiktionary() -> dict[str, dict]:
    """Parse Wiktionary JSONL, grouping entries by word.

    Multiple entries per word (different POS) are merged into one record
    with a combined definitions_json list.
    """
    words = {}

    with open(WIKTIONARY_FILE) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            word_text = entry.get("word")
            if not word_text:
                continue
            word_key = word_text.lower()

            pos = entry.get("pos", "")
            senses = entry.get("senses", [])
            sounds = entry.get("sounds", [])

            # Extract definitions from this entry
            entry_defs = []
            entry_synonyms = set()
            entry_antonyms = set()
            for sense in senses:
                glosses = sense.get("glosses", [])
                if not glosses:
                    continue
                examples = sense.get("examples", [])
                example_text = examples[0].get("text") if examples else None
                entry_defs.append({
                    "part_of_speech": pos,
                    "definition": glosses[0],
                    "example": example_text,
                })
                for syn in sense.get("synonyms", []):
                    if isinstance(syn, dict) and "word" in syn:
                        entry_synonyms.add(syn["word"])
                for ant in sense.get("antonyms", []):
                    if isinstance(ant, dict) and "word" in ant:
                        entry_antonyms.add(ant["word"])

            if not entry_defs:
                continue

            # Extract phonetic and audio
            phonetic = None
            audio_url = None
            for s in sounds:
                if s.get("ipa") and not phonetic:
                    phonetic = s["ipa"]
                if s.get("audio") and not audio_url:
                    audio_url = s["audio"]

            if word_key not in words:
                # First entry for this word
                words[word_key] = {
                    "word": word_key,
                    "part_of_speech": pos,
                    "definition": entry_defs[0]["definition"],
                    "definitions_json": entry_defs,
                    "example_sentence": entry_defs[0].get("example"),
                    "phonetic": phonetic,
                    "audio_url": audio_url,
                    "synonyms": entry_synonyms,
                    "antonyms": entry_antonyms,
                }
            else:
                # Merge additional POS entries
                existing = words[word_key]
                existing["definitions_json"].extend(entry_defs)
                existing["synonyms"].update(entry_synonyms)
                existing["antonyms"].update(entry_antonyms)
                if not existing["phonetic"] and phonetic:
                    existing["phonetic"] = phonetic
                if not existing["audio_url"] and audio_url:
                    existing["audio_url"] = audio_url

    # Finalize: convert sets to lists, limit synonyms/antonyms
    for w in words.values():
        w["synonyms"] = list(w["synonyms"])[:20]
        w["antonyms"] = list(w["antonyms"])[:20]

    logger.info(f"Parsed {len(words)} unique words from Wiktionary")
    return words


async def seed_wiktionary(db: AsyncSession) -> None:
    wikt_words = parse_wiktionary()
    classifications = load_classifications()
    freq_ranks = load_frequency_ranks()

    total = len(wikt_words)
    logger.info(f"Seeding {total} words from Wiktionary...")

    created = 0
    updated = 0
    pool_added = 0

    for i, (word_key, wikt) in enumerate(wikt_words.items(), 1):
        # Look up classification and frequency
        classification = classifications.get(word_key, {})
        cefr = classification.get("cefr")
        topics = classification.get("topics", [])
        freq_rank = freq_ranks.get(word_key)

        # Determine difficulty band
        if cefr:
            difficulty_band = cefr_to_difficulty_band(cefr)
        elif freq_rank:
            from app.utils.difficulty import assign_difficulty_band
            difficulty_band = assign_difficulty_band(freq_rank)
        else:
            difficulty_band = "C1-C2"

        # Build audio URL
        audio_url = None
        if wikt.get("audio_url"):
            audio_url = f"{WIKTIONARY_AUDIO_BASE}/{wikt['audio_url']}"

        # Check if word already exists
        result = await db.execute(select(Word).where(Word.word == word_key))
        word = result.scalar_one_or_none()

        if not word:
            word = Word(
                word=word_key,
                phonetic=wikt.get("phonetic"),
                audio_url=audio_url,
                definition=wikt["definition"],
                definitions_json=wikt["definitions_json"],
                example_sentence=wikt.get("example_sentence"),
                synonyms=wikt["synonyms"],
                antonyms=wikt["antonyms"],
                topics=topics,
                part_of_speech=wikt.get("part_of_speech"),
                frequency_rank=freq_rank,
                difficulty_band=difficulty_band,
                is_enriched=True,
                enriched_at=datetime.now(timezone.utc),
            )
            db.add(word)
            await db.flush()
            created += 1
        else:
            # Update existing word with Wiktionary data if not already enriched
            if not word.is_enriched:
                word.phonetic = wikt.get("phonetic") or word.phonetic
                word.audio_url = audio_url or word.audio_url
                word.definition = wikt["definition"]
                word.definitions_json = wikt["definitions_json"]
                word.example_sentence = wikt.get("example_sentence") or word.example_sentence
                word.synonyms = wikt["synonyms"] or word.synonyms
                word.antonyms = wikt["antonyms"] or word.antonyms
                word.topics = topics or word.topics
                word.part_of_speech = wikt.get("part_of_speech") or word.part_of_speech
                word.is_enriched = True
                word.enriched_at = datetime.now(timezone.utc)
                updated += 1
            # Always update frequency rank and difficulty band if available
            if freq_rank and not word.frequency_rank:
                word.frequency_rank = freq_rank
            if difficulty_band and word.difficulty_band != difficulty_band:
                word.difficulty_band = difficulty_band
            await db.flush()

        # Add to word pool
        pool_exists = await db.execute(
            select(WordPool).where(
                WordPool.word_id == word.id,
                WordPool.source == "wiktionary",
            )
        )
        if not pool_exists.scalar_one_or_none():
            db.add(WordPool(
                word_id=word.id,
                source="wiktionary",
                source_rank=freq_rank,
            ))
            pool_added += 1

        if i % COMMIT_BATCH_SIZE == 0:
            await db.commit()
            logger.info(
                f"Progress: {i}/{total} ({created} created, {updated} updated, "
                f"{pool_added} pool entries)"
            )

    await db.commit()
    logger.info(
        f"Wiktionary seeding done: {created} created, {updated} updated, "
        f"{pool_added} pool entries added"
    )


async def seed_topic_pack(db: AsyncSession, pack_name: str, filename: str) -> None:
    pack_file = DATA_DIR / "topic_packs" / filename
    if not pack_file.exists():
        logger.info(f"Topic pack not found, skipping: {pack_file}")
        return

    words = pack_file.read_text().strip().split("\n")
    source = f"topic_{pack_name}"
    logger.info(f"Seeding {len(words)} words from topic pack '{pack_name}'...")

    count = 0
    for rank, word_text in enumerate(words, start=1):
        word_text = word_text.strip().lower()
        if not word_text:
            continue

        existing = await db.execute(
            select(Word).where(Word.word == word_text)
        )
        word = existing.scalar_one_or_none()
        if not word:
            word = Word(word=word_text, difficulty_band="B2-C1")
            db.add(word)
            await db.flush()

        pool_exists = await db.execute(
            select(WordPool).where(
                WordPool.word_id == word.id,
                WordPool.source == source,
            )
        )
        if not pool_exists.scalar_one_or_none():
            db.add(WordPool(word_id=word.id, source=source, source_rank=rank))
            count += 1

    await db.commit()
    logger.info(f"Seeded {count} new words from topic pack '{pack_name}'")


async def main() -> None:
    async with async_session_factory() as db:
        await seed_wiktionary(db)

        topic_packs = {
            "academic": "academic.txt",
            "business": "business.txt",
            "technology": "technology.txt",
            "everyday": "everyday.txt",
        }
        for name, filename in topic_packs.items():
            await seed_topic_pack(db, name, filename)

    logger.info("Done!")


if __name__ == "__main__":
    asyncio.run(main())
