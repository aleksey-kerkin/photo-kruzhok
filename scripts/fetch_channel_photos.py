"""Download 24 Telegram channel JPEGs once. Not used by seed_demo."""

import html as html_module
import io
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "apps" / "api" / "fixtures" / "photos"
CHANNEL_URL = "https://t.me/s/PostSovietPhotography"
USER_AGENT = "PhotoKruzhokDemo/1.0"
COUNT = 24
LONG_EDGE = 480
DEFAULT_AUTHOR = "PostSovietPhotography"
LICENSE_LINE = (
    "channel owner permitted this demo, including WebP/AVIF derivatives"
)

MESSAGE_WRAP_SPLIT = '<div class="tgme_widget_message_wrap'
TEXT_RE = re.compile(
    r'tgme_widget_message_text[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
PHOTO_RE = re.compile(
    r'href="(https://t\.me/[^"]+)"[^>]*background-image:url\(\'([^\']+)\'\)',
)


def strip_html(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    return html_module.unescape(text).strip()


def parse_page(page_html: str) -> list[tuple[str, str, str | None]]:
    entries: list[tuple[str, str, str | None]] = []
    for chunk in page_html.split(MESSAGE_WRAP_SPLIT)[1:]:
        author = None
        text_match = TEXT_RE.search(chunk)
        if text_match:
            author = strip_html(text_match.group(1)) or None
        for message_url, image_url in PHOTO_RE.findall(chunk):
            entries.append((image_url, message_url, author))
    return entries


def prev_page_url(page_html: str) -> str | None:
    match = re.search(r'<link rel="prev" href="([^"]+)"', page_html)
    if not match:
        return None
    href = match.group(1)
    if href.startswith("http"):
        return href
    return "https://t.me" + href


def fetch_page(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode()


def collect_entries() -> list[tuple[str, str, str]]:
    page_url: str | None = CHANNEL_URL
    seen_images: set[str] = set()
    collected: list[tuple[str, str, str]] = []

    while page_url and len(collected) < COUNT:
        page_html = fetch_page(page_url)
        for image_url, message_url, author_text in parse_page(page_html):
            if image_url in seen_images:
                continue
            seen_images.add(image_url)
            author = author_text or DEFAULT_AUTHOR
            collected.append((image_url, message_url, author))
            if len(collected) >= COUNT:
                break
        if len(collected) >= COUNT:
            break
        page_url = prev_page_url(page_html)

    return collected


def download_image(url: str) -> Image.Image:
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            image.thumbnail((LONG_EDGE, LONG_EDGE))
            return image
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise last_error  # type: ignore[misc]


def main() -> None:
    entries = collect_entries()
    if len(entries) < COUNT:
        print(
            f"BLOCKED: need {COUNT} distinct channel photos, found {len(entries)}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    FIXTURES.mkdir(parents=True, exist_ok=True)
    lines = ["# Photo fixture credits", ""]
    for index, (image_url, message_url, author) in enumerate(entries[:COUNT], start=1):
        name = f"{index:02d}.jpg"
        image = download_image(image_url)
        image.save(FIXTURES / name, format="JPEG", quality=85)
        lines.extend(
            [
                f"## {name}",
                f"- Source: {message_url}",
                f"- Author: {author}",
                f"- License: {LICENSE_LINE}",
                "",
            ]
        )
    (FIXTURES / "CREDITS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
