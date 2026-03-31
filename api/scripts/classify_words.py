"""Classify Wiktionary words by CEFR level and topic using OpenRouter API.

Usage:
    OPENROUTER_API_KEY=sk-... uv run python -m scripts.classify_words
    OPENROUTER_API_KEY=sk-... OPENROUTER_MODEL=deepseek/deepseek-v3.2 uv run python -m scripts.classify_words

Supports resume: skips words already in the output file.
Runs 10 concurrent requests for speed.
"""

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
WIKTIONARY_FILE = DATA_DIR / "simple-extract.jsonl"
OUTPUT_FILE = DATA_DIR / "wiktionary_classified.jsonl"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-v3.2"

BATCH_SIZE = 100
CONCURRENCY = 20
MAX_RETRIES = 3

SYSTEM_PROMPT = """You are a linguist classifying English words by CEFR level and topic.

For each word, assign:
1. A CEFR level: A1, A2, B1, B2, C1, or C2
2. 1-3 topic tags from this list: general, academic, business, technology, science, medicine, law, arts, food, sports, travel, nature, emotions, body, clothing, household, politics, religion, slang

CEFR guidelines:
- A1: beginner essentials (hello, water, house, go, big, eat, red)
- A2: basic everyday (breakfast, airport, weather, buy, angry, kitchen)
- B1: intermediate (opportunity, appointment, recommend, essential, confident)
- B2: upper intermediate (acknowledge, consequence, sustainable, compromise)
- C1: advanced (scrutinize, relinquish, pragmatic, ubiquitous, meticulous)
- C2: proficiency (esoteric, perfunctory, obsequious, sesquipedalian)

Respond ONLY with a JSON array, no markdown fences, no explanation:
[{"word":"...","cefr":"...","topics":["..."]},...]"""


def load_wiktionary_words() -> list[str]:
    """Load unique lowercase words from Wiktionary JSONL."""
    words = set()
    with open(WIKTIONARY_FILE) as f:
        for line in f:
            obj = json.loads(line)
            w = obj.get("word")
            if w:
                words.add(w.lower())
    return sorted(words)


def load_already_classified() -> set[str]:
    """Load words already in the output file (for resume support)."""
    classified = set()
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    classified.add(obj["word"].lower())
                except (json.JSONDecodeError, KeyError):
                    continue
    return classified


def parse_response(text: str) -> list[dict]:
    """Parse the LLM response into a list of classification dicts."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        items = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            items = json.loads(match.group())
        else:
            raise

    valid_cefr = {"A1", "A2", "B1", "B2", "C1", "C2"}
    results = []
    for item in items:
        word = item.get("word", "").lower().strip()
        cefr = item.get("cefr", "").upper().strip()
        topics = item.get("topics", [])

        if not word or cefr not in valid_cefr:
            continue

        if not isinstance(topics, list):
            topics = [str(topics)]
        topics = [t.lower().strip() for t in topics if isinstance(t, str)]

        results.append({"word": word, "cefr": cefr, "topics": topics})

    return results


async def classify_batch(
    http_client: httpx.AsyncClient,
    words: list[str],
    model: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
    write_lock: asyncio.Lock,
    out_file,
    batch_idx: int,
    total_batches: int,
    counters: dict,
) -> None:
    """Send a batch of words to OpenRouter for classification and write results."""
    word_list = ", ".join(words)
    user_prompt = f"Classify these words:\n{word_list}"

    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                response = await http_client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.1,
                    },
                    timeout=120.0,
                )

                if response.status_code == 429:
                    wait = (attempt + 1) * 15
                    logger.warning(
                        f"Batch {batch_idx + 1}: rate limited, waiting {wait}s..."
                    )
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                results = parse_response(content)

                classified_words = {r["word"] for r in results}
                missed = [w for w in words if w not in classified_words]

                # Write results immediately under lock
                async with write_lock:
                    for item in results:
                        out_file.write(json.dumps(item, ensure_ascii=False) + "\n")
                    out_file.flush()
                    counters["classified"] += len(results)
                    counters["failed"] += len(missed)
                    counters["batches_done"] += 1

                logger.info(
                    f"Batch {batch_idx + 1}/{total_batches}: "
                    f"+{len(results)} classified"
                    + (f", {len(missed)} missed" if missed else "")
                    + f" | total: {counters['classified']} done, "
                    f"{counters['batches_done']}/{total_batches} batches"
                )
                return

            except httpx.HTTPError as e:
                logger.warning(
                    f"Batch {batch_idx + 1}: HTTP error (attempt {attempt + 1}): {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep((attempt + 1) * 5)
                continue
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning(
                    f"Batch {batch_idx + 1}: parse error (attempt {attempt + 1}): {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(2)
                continue

    logger.error(f"Batch {batch_idx + 1}: failed after {MAX_RETRIES} retries")
    async with write_lock:
        counters["failed"] += len(words)
        counters["batches_done"] += 1


async def main() -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    concurrency = int(os.environ.get("CONCURRENCY", str(CONCURRENCY)))

    logger.info(f"Loading Wiktionary words from {WIKTIONARY_FILE}...")
    all_words = load_wiktionary_words()
    logger.info(f"Total unique words: {len(all_words)}")

    already_done = load_already_classified()
    remaining = [w for w in all_words if w not in already_done]
    logger.info(f"Already classified: {len(already_done)}, remaining: {len(remaining)}")

    if not remaining:
        logger.info("All words already classified!")
        return

    # Split into batches
    batches = []
    for i in range(0, len(remaining), BATCH_SIZE):
        batches.append(remaining[i : i + BATCH_SIZE])

    total_batches = len(batches)
    logger.info(
        f"Processing {total_batches} batches with concurrency={concurrency}..."
    )

    semaphore = asyncio.Semaphore(concurrency)
    write_lock = asyncio.Lock()
    counters = {"classified": 0, "failed": 0, "batches_done": 0}

    async with httpx.AsyncClient() as http_client:
        with open(OUTPUT_FILE, "a") as out_f:
            tasks = [
                classify_batch(
                    http_client, batch, model, api_key,
                    semaphore, write_lock, out_f,
                    idx, total_batches, counters,
                )
                for idx, batch in enumerate(batches)
            ]
            await asyncio.gather(*tasks)

    logger.info(
        f"Done! classified={counters['classified']}, failed={counters['failed']}, "
        f"total_in_output={len(already_done) + counters['classified']}"
    )


if __name__ == "__main__":
    asyncio.run(main())
