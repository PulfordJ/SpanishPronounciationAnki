"""Generate sample TTS audio for one flashcard across edge-tts and gTTS,
in European (es_ES) and Latin American (es_US/MX) accents.

Run inside the Nix shell defined alongside this file:
    nix-shell tts_samples/shell.nix --run "python tts_samples/generate_samples.py"
"""

import asyncio
import os

PHRASE = "En mi ciudad hay un castillo"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


async def gen_edge():
    import edge_tts
    jobs = [
        ("sample_edge_es_ES.mp3", "es-ES-ElviraNeural"),   # European Spanish
        ("sample_edge_es_US.mp3", "es-MX-DaliaNeural"),    # Latin American (Mexico)
    ]
    for filename, voice in jobs:
        path = os.path.join(OUT_DIR, filename)
        await edge_tts.Communicate(PHRASE, voice).save(path)
        print(f"edge-tts  -> {filename}  ({voice})")


def gen_gtts():
    from gtts import gTTS
    jobs = [
        ("sample_gtts_es_ES.mp3", "es", "es"),       # European Spanish (tld=es)
        ("sample_gtts_es_US.mp3", "es", "com.mx"),   # Latin American (tld=com.mx)
    ]
    for filename, lang, tld in jobs:
        path = os.path.join(OUT_DIR, filename)
        gTTS(PHRASE, lang=lang, tld=tld).save(path)
        print(f"gTTS      -> {filename}  (lang={lang}, tld={tld})")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"Phrase: {PHRASE!r}  (mode={mode})\n")
    if mode in ("all", "edge"):
        asyncio.run(gen_edge())
    if mode in ("all", "gtts"):
        gen_gtts()
    print("\nDone.")
