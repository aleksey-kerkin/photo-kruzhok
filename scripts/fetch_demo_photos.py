"""Download 24 credited demo JPEGs. Not used by seed_demo."""

import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "apps" / "api" / "fixtures" / "photos"
LANDING = ROOT / "apps" / "web" / "public" / "photos"
COUNT = 24
LONG_EDGE = 480

API = "https://commons.wikimedia.org/w/api.php"
QUERY = {
    "action": "query",
    "format": "json",
    "generator": "search",
    "gsrsearch": 'filetype:bitmap incategory:"CC-Zero"',
    "gsrnamespace": "6",
    "gsrlimit": "40",
    "prop": "imageinfo",
    "iiprop": "url|extmetadata|mime",
    "iiurlwidth": str(LONG_EDGE),
}


def main():
    request = urllib.request.Request(API + "?" + urllib.parse.urlencode(QUERY))
    request.add_header("User-Agent", "PhotoKruzhokDemo/1.0 (portfolio demo)")
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    pages = list(payload["query"]["pages"].values())
    chosen = []
    for page in pages:
        info = page.get("imageinfo", [{}])[0]
        if info.get("mime") != "image/jpeg":
            continue
        meta = info.get("extmetadata", {})
        license_name = meta.get("LicenseShortName", {}).get("value", "")
        upper = license_name.upper()
        allowed = "CC0" in upper or "CC ZERO" in upper or "PUBLIC DOMAIN" in upper
        if not allowed or "ND" in upper:
            continue
        artist = meta.get("Artist", {}).get("value", "Unknown")
        chosen.append((info["thumburl"], artist, license_name, page.get("title", "")))
        if len(chosen) == COUNT:
            break
    if len(chosen) != COUNT:
        raise SystemExit(f"Need {COUNT} JPEGs, found {len(chosen)}")

    FIXTURES.mkdir(parents=True, exist_ok=True)
    LANDING.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Photo fixture credits",
        "",
        "Each file is a resized photograph. The license allows git storage,",
        "non-commercial demo display, and WebP/AVIF derivatives.",
        "",
    ]
    for index, (url, artist, license_name, title) in enumerate(chosen, start=1):
        name = f"{index:02d}.jpg"
        image_request = urllib.request.Request(url)
        image_request.add_header("User-Agent", "PhotoKruzhokDemo/1.0 (portfolio demo)")
        with urllib.request.urlopen(image_request, timeout=60) as response:
            raw = response.read()
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        image.thumbnail((LONG_EDGE, LONG_EDGE))
        target = FIXTURES / name
        image.save(target, format="JPEG", quality=85)
        if index <= 3:
            image.save(LANDING / name, format="JPEG", quality=85)
        lines.extend(
            [
                f"## {name}",
                f"- Source: {title}",
                f"- Author: {artist}",
                f"- License: {license_name}",
                "",
            ]
        )
    (FIXTURES / "CREDITS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
