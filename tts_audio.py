"""Text-to-speech audio generation for the Spanish Pronunciation deck.

Generates one MP3 per (Spanish phrase, accent) using Microsoft edge-tts and
caches them on disk so re-runs only synthesize phrases that don't yet have
audio. Filenames are content-addressed (hash of the text + accent), so the same
phrase always maps to the same file and is shared across decks. This is the
"only run TTS for cards that don't have audio yet" cache.

Run standalone to (re)populate the cache:
    uv run python tts_audio.py
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import sys
import tempfile
from pathlib import Path

# Accent key -> edge-tts neural voice.
VOICES = {
    "es_ES": "es-ES-ElviraNeural",  # European Spanish
    "es_US": "es-MX-DaliaNeural",  # Latin American Spanish (Mexico)
}

# Filenames are namespaced so they don't collide with other media in a user's
# Anki collection when the deck is imported.
MEDIA_PREFIX = "spt_"

CACHE_DIR = Path(__file__).resolve().parent / "tts_cache"

# Concurrency + resilience knobs for the (network-bound) edge-tts calls.
_CONCURRENCY = 10
_RETRIES = 3


def audio_filename(text: str, voice_key: str) -> str:
    """Deterministic media filename for a phrase in a given accent."""
    digest = hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:16]
    return f"{MEDIA_PREFIX}{voice_key}_{digest}.mp3"


def cache_path(text: str, voice_key: str) -> Path:
    return CACHE_DIR / audio_filename(text, voice_key)


def collect_unique_spanish() -> list[str]:
    """All unique, non-empty Spanish phrases across every deck in decks_data."""
    from decks_data import decks

    seen = set()
    for cards in decks.values():
        for _english, spanish in cards:
            s = spanish.strip()
            if s:
                seen.add(s)
    return sorted(seen)


async def _synthesize(text: str, voice_key: str) -> None:
    """Synthesize one file if it isn't already cached (atomic write)."""
    import edge_tts

    dest = cache_path(text, voice_key)
    if dest.exists() and dest.stat().st_size > 0:
        return  # cached -> skip

    last_err: Exception | None = None
    for attempt in range(1, _RETRIES + 1):
        fd, tmp = tempfile.mkstemp(suffix=".mp3", dir=CACHE_DIR)
        os.close(fd)
        try:
            await edge_tts.Communicate(text, VOICES[voice_key]).save(tmp)
            if os.path.getsize(tmp) == 0:
                raise RuntimeError("edge-tts produced an empty file")
            os.replace(tmp, dest)  # atomic: only a complete file lands in cache
            return
        except Exception as err:  # noqa: BLE001 - retry any transient TTS error
            last_err = err
            try:
                os.remove(tmp)
            except OSError:
                pass
            if attempt < _RETRIES:
                await asyncio.sleep(attempt)
    raise RuntimeError(f"Failed to synthesize {text!r} ({voice_key}): {last_err}")


async def _generate(texts: list[str]) -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pending = [
        (t, vk) for t in texts for vk in VOICES if not cache_path(t, vk).exists()
    ]
    sem = asyncio.Semaphore(_CONCURRENCY)

    async def _bounded(t: str, vk: str) -> None:
        async with sem:
            await _synthesize(t, vk)

    await asyncio.gather(*(_bounded(t, vk) for t, vk in pending))
    return len(pending)


def generate_missing(texts) -> dict:
    """Synthesize audio for any (phrase, accent) not already cached.

    Returns counts so callers can report what happened.
    """
    texts = sorted({t.strip() for t in texts if t and t.strip()})
    total = len(texts) * len(VOICES)
    generated = asyncio.run(_generate(texts))
    return {"total": total, "generated": generated, "cached": total - generated}


def main() -> None:
    texts = collect_unique_spanish()
    files = len(texts) * len(VOICES)
    print(f"Unique phrases: {len(texts)} x {len(VOICES)} accents = {files} files")
    print(f"Cache dir: {CACHE_DIR}")
    stats = generate_missing(texts)
    print(f"Generated {stats['generated']} new file(s); {stats['cached']} already cached.")


if __name__ == "__main__":
    main()
