#!/usr/bin/env python3
"""Deterministic source and local-HTTP checks for the isolated V3 prototype."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
PAGES = [INDEX]
KILLED = [
    "Explore treadmill",
    "No Explore feed",
    "No algorithmic Home ranking",
    "No public scoreboards",
    "Attention you can finish",
    "Not an endless stream",
]
CAPTURE_PATHS = (
    "assets/story/beat-1-knock.png",
    "assets/story/beat-2-cover.png",
    "assets/story/beat-3-grid.png",
    "assets/story/beat-4-post.png",
    "assets/story/beat-5-reply.png",
    "assets/story/beat-6-done.png",
    "assets/people/messages.png",
)
PLACEHOLDER_SHA256 = {
    "046853569adfcbe5fb2191360b5f6ff74c1295c665a306c2952f4a6f8fbbbbf1",
    "671be4397c7182af89d0d5251f7803d295002ebf555444dcf8a9d04b2e7c22fe",
    "f24668ba6fc9aa3a87bf49e9056b09bb145c9de506af4647b81f446f4a38d529",
    "23f8b219159a673025769e70ae4e6a22d6349400c54d77d33eadb276d5530aa6",
    "d651505c3395ee678fab732ba231dec55a46b8630973933da16a09edc414ed74",
    "35dfde63929c1c8609548f82034d92d48b7eefde9a4b41a7eeca18366011299e",
    "72e70eec2734df92ab4d2c31d882e38ada4b13a9be32b2547d0b0d0d4f3310ac",
}
REQUIRED_COPY = [
    "A week worth opening.",
    "Pixeldrop is a photo app with a weekly rhythm. Gather moments as they happen. Then, once a week, the Drop opens for the people you've chosen, all at once. Read the week, reply to the people you love, and be done.",
    "See a week open",
    "How it's built",
    "One Drop, start to finish",
    "Ten minutes, once a week.",
    "This is the whole loop: what opens, what you see, and the ending you actually reach.",
    "The Drop is ready",
    "One notification a week. This is it.",
    "The week opens",
    "Like something wrapped. You can already see the shape of it.",
    "Everyone, once",
    "The whole week in one view. No ranking, no refresh. Just your people.",
    "Reading",
    "Photos stay photos. The caption rests underneath, like a note.",
    "Answering",
    "Say it to the person, not the room.",
    "The ending",
    "Done for now. Back to your Friday.",
    "That's the product. It happens once a week, and it ends.",
    "Who it's for",
    "Made for the people you'd hand your phone to.",
    "Circles",
    "Group your people the way you actually think of them: family, the group chat, old friends. Every moment you share is for the circles you choose, and your choices stay yours. Nobody sees how you've organized the people in your life.",
    "Private replies",
    "The first way to respond is a message to the person, with their moment attached. Conversations start where they'd naturally happen, between the two of you.",
    "Places for memory",
    "Profiles and collections hold what's worth keeping. A drop ends. The things you loved in it don't disappear.",
    "Messages",
    "Every drop starts conversations. Messages keeps them in one place: private replies arrive with the moment attached, so you both know exactly what you're talking about.",
    "Built small, on purpose.",
    "One person, many tools.",
    "Pixeldrop is currently built by one person, with a lot of help from AI. The code gets written fast. The decisions about what this app values, and what it will never do to the people using it, stay human.",
    "No tracking, no ad machine.",
    "Pixeldrop does not profile you and is not built to sell your attention. The long-term plan is federation: many small servers run by people, like personal blogs or group chats. Small servers do not need ads to survive, and this one never will.",
    "What's ahead, plainly.",
    "A small private beta is running now. A public beta is targeted for September 2026. Open source and federation come after the core is stable and reviewed. If any of this changes, this page will change with it.",
    "Where things stand",
    "A small first group is using Pixeldrop now.",
    "Pixeldrop is in private beta with a handful of people, opening real weekly drops together. This stage is deliberately small: the weekly ritual has to feel right for ten people before it can mean anything for more.",
    "What's a Drop?",
    "One shared week. Everyone gathers moments as the week happens. On Friday evening the week opens for everyone at once. You read it start to finish. There's a beginning and an end.",
    "When does the Drop open?",
    "Friday evening, for everyone on the same rhythm. Half the point is knowing the people you love are opening the same week you are.",
    "What are Circles and the Lens?",
    "Circles are how you group your people. Every moment is shared to the circles you choose. The Lens is your own viewing filter. See just family, or just the friends you're missing, without your choices ever being visible to anyone else.",
    "How is this different from the feeds I already have?",
    "Mostly by rhythm and ending. Nothing here is ranked or engineered to keep you scrolling. The week has a shape, you reach the end of it, and the app is designed to be put down. Pixeldrop isn't trying to replace anything. It's trying to be the best place for the moments that matter to a smaller set of people.",
    "Can I use it?",
    "Not yet, unless you're in the first beta group. Pixeldrop is deliberately small right now while the weekly ritual gets proven with real people. A public beta is targeted for September 2026.",
    "Say hello",
    "General interest, beta questions, or want to help build Pixeldrop? Reach out: admin@pixeldrop.social",
    "No analytics or third-party runtime requests",
]


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.resources: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.headings: list[int] = []
        self.lang: str | None = None
        self.summary_count = 0
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs_raw: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_raw)
        if tag == "html":
            self.lang = attrs.get("lang")
        if attrs.get("id"):
            self.ids.add(str(attrs["id"]))
        if tag == "a":
            self.links.append(attrs.get("href") or "")
        if tag == "img":
            self.resources.append(attrs.get("src") or "")
            self.images.append({"src": attrs.get("src"), "alt": attrs.get("alt")})
        if tag in {"link", "script"}:
            resource = attrs.get("href") or attrs.get("src")
            if resource:
                self.resources.append(resource)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag == "summary":
            self.summary_count += 1

    def handle_data(self, data: str) -> None:
        self._text.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self._text).split())


def parse(path: Path) -> Parser:
    parser = Parser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def resolve(page: Path, raw: str) -> tuple[Path, str]:
    path_part, fragment = urldefrag(raw)
    return (page if not path_part else (page.parent / path_part).resolve()), fragment


def png_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()[:24]
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not PNG: {path.name}")
    return int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")


def main() -> int:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--base-url", default="")
    args = argument_parser.parse_args()
    failures: list[str] = []

    def check(label: str, function) -> None:
        try:
            detail = function()
            print(f"PASS {label}" + (f" — {detail}" if detail else ""))
        except Exception as error:
            failures.append(f"{label}: {error}")
            print(f"FAIL {label} — {error}")

    parsers = {page: parse(page) for page in PAGES}

    def structure() -> str:
        for page, parser in parsers.items():
            if parser.lang != "en":
                raise AssertionError(f"{page.name}: lang is not en")
            if parser.headings.count(1) != 1:
                raise AssertionError(f"{page.name}: expected one h1")
            if any(level > previous + 1 for previous, level in zip(parser.headings, parser.headings[1:])):
                raise AssertionError(f"{page.name}: heading level jump")
            if any(image["alt"] is None for image in parser.images):
                raise AssertionError(f"{page.name}: image without alt")
        main_markup = re.search(r"<main\b.*?</main>", INDEX.read_text(encoding="utf-8"), re.S)
        if not main_markup or len(re.findall(r"<section\b", main_markup.group(0))) != 7:
            raise AssertionError("homepage must have seven main sections plus footer")
        if parsers[INDEX].summary_count != 5:
            raise AssertionError("homepage must have five FAQ details")
        return "seven main sections + footer; five native FAQ details; accessible images"

    check("Homepage architecture and source accessibility", structure)

    def approved_copy() -> str:
        text = parsers[INDEX].text
        missing = [value for value in REQUIRED_COPY if value not in text]
        if missing:
            raise AssertionError(f"missing/changed approved copy: {missing}")
        return f"{len(REQUIRED_COPY)} approved strings present verbatim"

    check("Approved homepage copy", approved_copy)

    def killed_copy() -> str:
        public_source = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".html", ".css", ".js", ".md", ".txt"})
        hits = [phrase for phrase in KILLED if phrase in public_source]
        removed_phrases = ["support" + ".html", "In private " + "beta", "Follow " + "the build"]
        hits.extend(phrase for phrase in removed_phrases if phrase in public_source)
        if hits:
            raise AssertionError(f"killed copy survives: {hits}")
        if parsers[INDEX].text.count("—") > 3:
            raise AssertionError("rendered copy contains more than three em dashes")
        return f"all removed phrases absent; {parsers[INDEX].text.count('—')} rendered em dashes"

    check("Killed-copy grep", killed_copy)

    def references() -> str:
        checked = 0
        for page, parser in parsers.items():
            for raw in parser.links + parser.resources:
                if not raw:
                    raise AssertionError(f"{page.name}: empty reference")
                parsed = urlparse(raw)
                if parsed.scheme == "mailto" and raw == "mailto:admin@pixeldrop.social":
                    checked += 1
                    continue
                if parsed.scheme or raw.startswith("//"):
                    raise AssertionError(f"{page.name}: external runtime reference {raw}")
                target, fragment = resolve(page, raw)
                if not target.exists():
                    raise AssertionError(f"{page.name}: missing {raw}")
                if fragment:
                    target_parser = parsers.get(target) or parse(target)
                    if fragment not in target_parser.ids:
                        raise AssertionError(f"{page.name}: missing fragment {raw}")
                checked += 1
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        for raw in re.findall(r"url\([\"']?([^\"')]+)", css):
            if urlparse(raw).scheme or raw.startswith("//"):
                raise AssertionError(f"external CSS reference {raw}")
            if not (ROOT / raw).resolve().exists():
                raise AssertionError(f"missing CSS asset {raw}")
            checked += 1
        if re.search(r"(?:fetch|XMLHttpRequest|sendBeacon)\s*\(", (ROOT / "story.js").read_text(encoding="utf-8")):
            raise AssertionError("network API found in story.js")
        return f"{checked} local references; no authored network API"

    check("Local-only runtime references", references)

    def real_captures() -> str:
        index = INDEX.read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        images_by_source = {str(image["src"]): image for image in parsers[INDEX].images if image["src"]}
        failures: list[str] = []
        seen_hashes: set[str] = set()

        for relative in CAPTURE_PATHS:
            path = ROOT / relative
            if not path.is_file():
                failures.append(f"missing stable capture path: {relative}")
                continue
            dimensions = png_dimensions(path)
            if dimensions != (1206, 2622):
                failures.append(f"wrong dimensions for {relative}: {dimensions}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in PLACEHOLDER_SHA256:
                failures.append(f"recorded placeholder hash at {relative}: {digest}")
            if digest in seen_hashes:
                failures.append(f"duplicate capture bytes at {relative}: {digest}")
            seen_hashes.add(digest)
            if index.count(f'src="{relative}"') != 1:
                failures.append(f"expected one exact local index reference: {relative}")
            image = images_by_source.get(relative)
            if image is None:
                failures.append(f"capture is not parsed as an image: {relative}")
            elif "placeholder" in str(image["alt"]).lower():
                failures.append(f"placeholder alt language survives: {relative}")

        actual_story_paths = tuple(
            path.relative_to(ROOT).as_posix()
            for path in sorted((ROOT / "assets/story").glob("beat-*.png"))
        )
        if actual_story_paths != CAPTURE_PATHS[:6]:
            failures.append(f"story capture inventory mismatch: {actual_story_paths}")
        if "placeholder" in readme.lower():
            failures.append("README still describes integrated captures as placeholders")
        if failures:
            raise AssertionError("; ".join(failures))
        return "seven exact local 1206×2622 PNG paths; recorded placeholders rejected"

    check("Real app capture contract", real_captures)

    def fallbacks() -> str:
        index = INDEX.read_text(encoding="utf-8")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        script = (ROOT / "story.js").read_text(encoding="utf-8")
        if index.count('class="phone-shell story-frame') != 6:
            raise AssertionError("six inline frames are not present in HTML")
        if "prefers-reduced-motion: reduce" not in css:
            raise AssertionError("reduced-motion CSS missing")
        if 'prefers-reduced-motion: no-preference' not in script or "min-width: 901px" not in script:
            raise AssertionError("JS enhancement is not gated by desktop and motion preference")
        if "scrollama()" not in script or "translateY(14px)" not in css or "translateY(-14px)" not in css:
            raise AssertionError("scrollama/crossfade-slide contract missing")
        if "66vh" not in css or "opacity 180ms" not in css or "opacity 220ms" not in css:
            raise AssertionError("tightened story timing contract missing")
        return "static source sequence; desktop-only motion enhancement; 66vh beats; short transitions"

    check("No-JS, reduced-motion, mobile, and scrollama source contract", fallbacks)

    def XML_docs() -> str:
        XML_docs = [ROOT / "sitemap.xml", *sorted((ROOT / "assets").glob("*.svg"))]
        for path in XML_docs:
            ET.parse(path)
        return f"{len(XML_docs)} XML/SVG files parsed"

    check("XML and SVG parsing", XML_docs)

    if args.base_url:
        def http_files() -> str:
            checked = 0
            for path in sorted(ROOT.rglob("*")):
                if not path.is_file() or "artifacts" in path.parts:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                with urllib.request.urlopen(f"{args.base_url.rstrip('/')}/{relative}", timeout=10) as response:
                    if response.status != 200:
                        raise AssertionError(f"HTTP {response.status}: {relative}")
                    response.read(32)
                checked += 1
            return f"{checked} files returned HTTP 200"
        check("Local HTTP assets", http_files)
    else:
        print("SKIP Local HTTP assets — provide --base-url")

    if failures:
        print("\nVERIFICATION FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nVERIFICATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
