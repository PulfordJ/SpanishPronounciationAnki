"""Measure edge-tts MP3 size vs. phrase length to fit a size model."""
import asyncio, os, tempfile

PHRASES = [
    "Irás",
    "we live",
    "un diario",
    "hojas de papel",
    "they have money (masc.)",
    "porque quiere vivir en costa rica",
    "Creo que Gonzalo es organizado porque su mesa es muy organizada",
]
VOICE = "es-ES-ElviraNeural"


async def main():
    import edge_tts
    rows = []
    for p in PHRASES:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        await edge_tts.Communicate(p, VOICE).save(path)
        size = os.path.getsize(path)
        os.remove(path)
        rows.append((len(p), size))
        print(f"{len(p):3d} chars -> {size:6d} bytes  ({p!r})")

    # least-squares linear fit: bytes = a + b*chars
    n = len(rows)
    sx = sum(c for c, _ in rows); sy = sum(s for _, s in rows)
    sxx = sum(c * c for c, _ in rows); sxy = sum(c * s for c, s in rows)
    b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    a = (sy - b * sx) / n
    print(f"\nfit: bytes = {a:.1f} + {b:.2f} * chars")
    print(f"FIT_A={a:.4f}")
    print(f"FIT_B={b:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
