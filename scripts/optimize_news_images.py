#!/usr/bin/env python3
"""Create lightweight editorial card thumbnails from selected already-linked press images.

This only handles explicitly reviewed source URLs. Keep copyright attribution and
original source links in articles. Do not treat a public image as a general reuse license.
"""
import io
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets/images/news"
# Explicit editorial-source allowlist, not arbitrary user-controlled image fetching.
SOURCES = {
    "yumeneko-connect-anime-announcement": "https://sh-anime.shochiku.co.jp/yumeconne-anime/og-image.jpg",
    "bleach-thousand-year-blood-war-graniph-collection-october-2026": "https://cf.graniph.com/images/category/collection_01419/2026100811141920261014_BLEACH_1200-1200.jpg",
}
HOSTS = {"sh-anime.shochiku.co.jp", "cf.graniph.com"}
MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 25_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

def download(url):
    if urlparse(url).hostname not in HOSTS or urlparse(url).scheme != "https":
        raise ValueError("Source not approved")
    request = Request(url, headers={"User-Agent": "AniNextUpEditorialImageOptimizer/1.0", "Accept": "image/*"})
    with urlopen(request, timeout=20) as response:
        if urlparse(response.url).hostname not in HOSTS:
            raise ValueError("Redirect to unapproved image host")
        if not response.headers.get("Content-Type", "").lower().startswith("image/"):
            raise ValueError("Response is not an image")
        if int(response.headers.get("Content-Length") or 0) > MAX_BYTES:
            raise ValueError("Image too large")
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Image too large")
        return data

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for slug, url in SOURCES.items():
        output = DEST / (slug + ".webp")
        if output.exists():
            print("Already optimized:", output.relative_to(ROOT))
            continue
        try:
            with Image.open(io.BytesIO(download(url))) as source:
                source.load()
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((480, 360), Image.Resampling.LANCZOS)
                image.save(output, "WEBP", quality=74, method=6)
            print("Optimized:", output.relative_to(ROOT), output.stat().st_size, "bytes")
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            print("Source unavailable; preserving external image:", slug, str(exc))
    # Update the server-rendered homepage fallback too, without touching its layout.
    homepage = ROOT / "index.html"
    if homepage.exists():
        text = homepage.read_text(encoding="utf-8")
        for slug, remote in SOURCES.items():
            if not (DEST / (slug + ".webp")).exists():
                continue
            # Only replace images in the card linking to the matching article.
            import re
            pattern = r'(<a class="card story visual-card" href="articles/' + re.escape(slug) + r'"><img src=")' + re.escape(remote) + r'(")'
            text, count = re.subn(pattern, lambda m: m.group(1) + "assets/images/news/" + slug + ".webp" + m.group(2), text)
            print("Updated homepage fallback:", slug, count)
        homepage.write_text(text, encoding="utf-8")
    print("Finished editorial thumbnails")

if __name__ == "__main__":
    main()
