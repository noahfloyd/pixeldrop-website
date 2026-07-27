#!/usr/bin/env python3
"""Generate the delivery assets: WebP captures and subset WOFF2 fonts.

The PNGs under assets/story/ and assets/people/ are the provenance originals:
verify.py pins their exact dimensions and SHA-256 digests. Browsers never load
them when WebP is supported. This script produces the WebP the page actually
serves, at identical pixel dimensions, so the delivered frame is the accepted
capture, only re-encoded.
"""
from pathlib import Path

from fontTools import subset
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
FONTS = [
    "assets/fonts/Fraunces-500.ttf",
    "assets/fonts/Fraunces-600.ttf",
    "assets/fonts/Inter-400.ttf",
    "assets/fonts/Inter-500.ttf",
    "assets/fonts/Inter-600.ttf",
]
# Generous Latin coverage: ASCII, Latin-1, Latin Extended-A, general punctuation
# (curly quotes, dashes, ellipsis), currency, arrows, and the fullwidth plus the
# FAQ markers use. verify.py fails if rendered copy ever leaves these ranges.
SUBSET_RANGES = [
    (0x0020, 0x007E), (0x00A0, 0x00FF), (0x0100, 0x017F),
    (0x2000, 0x206F), (0x20AC, 0x20AC), (0x2122, 0x2122),
    (0x2190, 0x2193), (0x2212, 0x2212), (0xFF0B, 0xFF0B),
]


def build_fonts() -> None:
    codepoints = [point for start, end in SUBSET_RANGES for point in range(start, end + 1)]
    total_ttf = total_woff2 = 0
    for relative in FONTS:
        source = ROOT / relative
        target = source.with_suffix(".woff2")
        options = subset.Options(flavor="woff2")
        options.name_IDs = ["*"]      # keep the OFL notice inside the font
        options.notdef_outline = True
        font = subset.load_font(str(source), options)
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=codepoints)
        subsetter.subset(font)
        subset.save_font(font, str(target), options)
        font.close()
        ttf_kb = source.stat().st_size / 1024
        woff2_kb = target.stat().st_size / 1024
        total_ttf += ttf_kb
        total_woff2 += woff2_kb
        print(f"{relative:38s} {ttf_kb:8.0f} KB -> {woff2_kb:7.0f} KB")
    print(f"{'TOTAL FONTS':38s} {total_ttf:8.0f} KB -> {total_woff2:7.0f} KB "
          f"({100 - total_woff2 / total_ttf * 100:.0f}% smaller)")


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
    print(f"{'TOTAL CAPTURES':38s} {total_png:8.0f} KB -> {total_webp:7.0f} KB "
          f"({100 - total_webp / total_png * 100:.0f}% smaller)")
    build_fonts()

if __name__ == "__main__":
    main()
