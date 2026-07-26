#!/usr/bin/env python3
"""Generate WebP delivery derivatives from the untouched PNG captures.

The PNGs under assets/story/ and assets/people/ are the provenance originals:
verify.py pins their exact dimensions and SHA-256 digests. Browsers never load
them when WebP is supported. This script produces the WebP the page actually
serves, at identical pixel dimensions, so the delivered frame is the accepted
capture, only re-encoded.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCES = [
    "assets/story/beat-1-knock.png",
    "assets/story/beat-2-cover.png",
    "assets/story/beat-3-grid.png",
    "assets/story/beat-4-post.png",
    "assets/story/beat-5-reply.png",
    "assets/story/beat-6-done.png",
    "assets/people/messages.png",
]
QUALITY = 80

def main() -> None:
    total_png = total_webp = 0
    for relative in SOURCES:
        source = ROOT / relative
        target = source.with_suffix(".webp")
        with Image.open(source) as image:
            image.convert("RGB").save(target, "WEBP", quality=QUALITY, method=6)
        png_kb = source.stat().st_size / 1024
        webp_kb = target.stat().st_size / 1024
        total_png += png_kb
        total_webp += webp_kb
        print(f"{relative:38s} {png_kb:8.0f} KB -> {webp_kb:7.0f} KB")
    print(f"{'TOTAL':38s} {total_png:8.0f} KB -> {total_webp:7.0f} KB "
          f"({100 - total_webp / total_png * 100:.0f}% smaller)")

if __name__ == "__main__":
    main()
