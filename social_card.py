#!/usr/bin/env python3
"""Render assets/social-card.png, the 1200x630 link preview image.

Uses the site's own fonts, colour tokens, and two accepted app captures, so the
card cannot drift from what the page itself shows.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets/social-card.png"
W, H = 1200, 630
NIGHT, RAISED = (9, 11, 16), (15, 19, 27)
TEXT, DIM, BLUE = (238, 242, 245), (132, 144, 156), (169, 209, 232)
FRAUNCES = str(ROOT / "assets/fonts/Fraunces-600.ttf")
INTER_500 = str(ROOT / "assets/fonts/Inter-500.ttf")
INTER_400 = str(ROOT / "assets/fonts/Inter-400.ttf")


def rounded(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, *image.size], radius, fill=255)
    image.putalpha(mask)
    return image


def phone(relative: str, height: int) -> Image.Image:
    with Image.open(ROOT / relative) as source:
        frame = source.convert("RGB")
    width = round(frame.width * height / frame.height)
    return rounded(frame.resize((width, height), Image.LANCZOS), 26)


def tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for character in text:
        draw.text((x, y), character, font=font, fill=fill)
        x += draw.textlength(character, font=font) + tracking


card = Image.new("RGB", (W, H), NIGHT)

# soft raised wash behind the artwork side
wash = Image.new("RGB", (W, H), NIGHT)
ImageDraw.Draw(wash).ellipse([600, -300, 1520, 760], fill=RAISED)
wash = wash.filter(ImageFilter.GaussianBlur(70))
card = Image.blend(card, wash, 0.9)
draw = ImageDraw.Draw(card)

# artwork: two accepted captures, back one tucked behind
back = phone("assets/story/beat-3-grid.png", 470)
front = phone("assets/story/beat-4-post.png", 560)
card.paste(back, (706, 62), back)
card.paste(front, (898, 98), front)

# copy
tracked(draw, (80, 132), "PIXELDROP", ImageFont.truetype(INTER_500, 24), DIM, 5)
headline = ImageFont.truetype(FRAUNCES, 82)
draw.text((78, 196), "A week worth", font=headline, fill=TEXT)
draw.text((78, 296), "opening.", font=headline, fill=BLUE)
body = ImageFont.truetype(INTER_400, 27)
draw.text((80, 438), "A photo app with a weekly rhythm.", font=body, fill=DIM)
draw.text((80, 476), "Once a week, the Drop opens for the", font=body, fill=DIM)
draw.text((80, 514), "people you've chosen, all at once.", font=body, fill=DIM)

card.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT.relative_to(ROOT)} {card.size} {OUT.stat().st_size/1024:.0f} KB")
