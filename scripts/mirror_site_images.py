#!/usr/bin/env python3
"""Mirror rendered site images into assets/images/external and rewrite references."""
from __future__ import annotations

import hashlib
import html
import io
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/images/external"
MAX_BYTES = 20 * 1024 * 1024
SITE_HOSTS = {"aninextup.com", "www.aninextup.com"}
TEXT_EXTENSIONS = {".html", ".js", ".json", ".css", ".svg"}
SKIP_DIRS = {".git", ".github", "node_modules", "scripts", "tests", "audits", "reports", "editorial-drafts"}
URL_RE = re.compile(r"(?:https?:)?//[^\s\"'<>),]+", re.I)

# Some legacy or hotlink-protected sources in the content have stopped serving
# images. These verified image URLs are replacements for the same visuals.
SOURCE_OVERRIDES = {
    "https://bless-anime.com/assets/img/top/visual/visual1-main.jpg":
        "https://img2.animatetimes.com/2026/03/953189380a8f51ee780a2a49a69690dc69aa7a7a892dd5_59053360_0fd2bafd5c8626dedc940b4db4e8b3f50b57a0fe.jpg",
    "https://en.dragon-ball-official.com/dragonball/en/news/2026/09/DBSBE_SurgeKV_en.jpg?_=1791070440":
        "https://dragonball-super.com/en/updates/img/20260903-1.jpg",
    "https://hyouken-anime.com/wp/wp-content/themes/hyouken-theme/images/kv1.webp":
        "https://cimg.kgl-systems.io/camion/files/84990/ogp_cTHd.jpg?x=1280",
    "https://i0.wp.com/anitrendz.net/news/wp-content/uploads/2026/09/ace-of-the-diamond-act-II-second-season-second-cour-new-visual.jpeg?ssl=1":
        "https://cimg.kgl-systems.io/camion/files/87131/ogp_WNsM.jpg?x=1280",
    "https://i0.wp.com/anitrendz.net/news/wp-content/uploads/2026/10/Manchuria-Opium-SquadFirst-Anime-Adaptation-Visual-EN.jpg?ssl=1":
        "https://cimg.kgl-systems.io/camion/files/dengeki/90002/a666340cd694ea563ac5b8a04ea66915e.jpg",
    "https://tokyo-revengers-anime.com/img/home/visual_10.jpg":
        "https://moca-news.net/article/2026/10/03/0200a00/%21img/%21tweet0.jpg",
}


def image_references(text: str) -> set[str]:
    """Return URLs used in image-bearing HTML tags, data fields, and CSS."""
    found: set[str] = set()
    for tag_match in re.finditer(r"<[a-z][^>]*>", text, re.I | re.S):
        tag = tag_match.group(0)
        name_match = re.match(r"<\s*([\w:-]+)", tag)
        if not name_match:
            continue
        name = name_match.group(1).lower()
        attrs = {m.group(1).lower(): m.group(3) for m in re.finditer(
            r"([\w:-]+)\s*=\s*([\"'])(.*?)\2", tag, re.S
        )}
        if name == "img":
            for key in ("src", "data-src", "data-lazy-src", "data-original"):
                if key in attrs:
                    found.update(URL_RE.findall(html.unescape(attrs[key])))
            for key in ("srcset", "data-srcset"):
                if key in attrs:
                    found.update(URL_RE.findall(html.unescape(attrs[key])))
        elif name == "source":
            for key in ("srcset", "data-srcset"):
                if key in attrs:
                    found.update(URL_RE.findall(html.unescape(attrs[key])))
        elif name == "video" and "poster" in attrs:
            found.update(URL_RE.findall(html.unescape(attrs["poster"])))
        elif name == "link" and "href" in attrs:
            rel = attrs.get("rel", "").lower()
            if "image_src" in rel or ("preload" in rel and attrs.get("as", "").lower() == "image"):
                found.update(URL_RE.findall(html.unescape(attrs["href"])))
        elif name == "meta":
            identity = (attrs.get("property", "") + " " + attrs.get("name", "") + " " + attrs.get("itemprop", "")).lower()
            if any(token in identity for token in ("og:image", "twitter:image", "image")) and "content" in attrs:
                found.update(URL_RE.findall(html.unescape(attrs["content"])))

    # Data files and JSON-LD use these keys; CSS backgrounds use url(...).
    for pattern in (
        r"(?:^|[{,\s])(?:[\"']?(?:image|thumbnailUrl|thumbnail_url|poster)[\"']?)\s*:\s*[\"']((?:https?:)?//[^\"']+)",
        r"url\(\s*[\"']?((?:https?:)?//[^\s\"')]+)",
    ):
        found.update(m.group(1) for m in re.finditer(pattern, text, re.I | re.M))
    return found


def local_site_path(url: str) -> str | None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in SITE_HOSTS:
        return None
    path = unquote(parsed.path).lstrip("/")
    candidate = ROOT / path
    return "/" + path if candidate.is_file() else url


def download_image(url: str) -> tuple[bytes, str, str]:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; AniNextUpImageMirror/1.0)",
        "Accept": "image/avif,image/webp,image/png,image/jpeg,image/gif,image/*;q=0.9,*/*;q=0.5",
    })
    with urlopen(req, timeout=35) as response:
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"image exceeds {MAX_BYTES} bytes")
    if content_type == "image/svg+xml" or raw.lstrip().startswith(b"<svg") or b"<svg" in raw[:512]:
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise ValueError("response is not valid SVG XML") from exc
        if root.tag.rsplit("}", 1)[-1].lower() != "svg":
            raise ValueError("SVG response has no <svg> root")
        return raw, ".svg", content_type
    try:
        image = Image.open(io.BytesIO(raw))
        image.verify()
        fmt = (image.format or "").lower()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError(f"response is not a valid image (MIME {content_type or 'missing'})") from exc
    extensions = {"jpeg": ".jpg", "png": ".png", "webp": ".webp", "gif": ".gif", "avif": ".avif", "bmp": ".bmp", "tiff": ".tif"}
    ext = extensions.get(fmt)
    if not ext:
        raise ValueError(f"unsupported image format/MIME: {fmt}/{content_type}")
    # Normalize large raster artwork to WebP to keep the Worker asset bundle lean.
    # Animated GIFs remain GIFs so their motion is preserved.
    if fmt != "gif":
        with Image.open(io.BytesIO(raw)) as image:
            image.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            optimized = io.BytesIO()
            image.save(optimized, format="WEBP", quality=84, method=6)
            raw, ext, content_type = optimized.getvalue(), ".webp", "image/webp"
    return raw, ext, content_type


def site_files() -> list[Path]:
    return [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_EXTENSIONS
            and not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)]


def main() -> int:
    files = site_files()
    originals = {p: p.read_text(encoding="utf-8") for p in files}
    refs: set[str] = set()
    for body in originals.values():
        refs.update(image_references(body))

    mapping: dict[str, str] = {}
    errors: list[tuple[str, str]] = []
    OUT.mkdir(parents=True, exist_ok=True)
    for index, source in enumerate(sorted(refs), 1):
        # Normalize HTML-escaped query separators before requesting the source.
        source = html.unescape(source)
        original = source
        source = SOURCE_OVERRIDES.get(source, source)
        if source.startswith("//"):
            source = "https:" + source
        local = local_site_path(source)
        if local:
            mapping[original] = local
            continue
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        existing = list(OUT.glob(digest + ".*"))
        if existing:
            mapping[original] = "/" + existing[0].relative_to(ROOT).as_posix()
            continue
        try:
            raw, ext, _mime = download_image(source)
            target = OUT / (digest + ext)
            target.write_bytes(raw)
            mapping[original] = "/" + target.relative_to(ROOT).as_posix()
            print(f"[{index}/{len(refs)}] mirrored {original} -> {mapping[original]} ({len(raw)} bytes)", flush=True)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append((original, str(exc)))
            print(f"[{index}/{len(refs)}] FAILED {original}: {exc}", flush=True)
        time.sleep(0.08)

    if errors:
        print("\nNo source files were rewritten because some images could not be verified:", file=sys.stderr)
        for source, error in errors:
            print(f"- {source}: {error}", file=sys.stderr)
        return 1

    changed = 0
    # Longest first avoids replacing a URL prefix before a URL with a query string.
    replacements = sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True)
    for path, body in originals.items():
        updated = body
        for source, target in replacements:
            updated = updated.replace(source, target)
            updated = updated.replace(html.escape(source, quote=False), target)
        if updated != body:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    manifest = {
        "count": len(mapping),
        "images": [{"source": source, "local": target} for source, target in sorted(mapping.items())],
    }
    (OUT / "sources.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Mirrored {len(mapping)} image URLs; updated {changed} site files.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
