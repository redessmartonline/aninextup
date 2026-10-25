#!/usr/bin/env python3
"""Generate latest news from actual article metadata, without manually editing homepage."""
# Runs on article changes and may also be started manually from GitHub Actions.
# Full Git history is required to sort same-day articles by publication commit time.
import html, json, re, subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
OUT = ROOT / "assets" / "latest-news.json"
# Keep this newly published, substantially updated guide visible on the homepage.
PINNED_ARTICLES = {"articles/returners-magic-season-2", "articles/sasaki-and-peeps-season-2"}

def meta(source, name):
    pattern = r'<meta\s+[^>]*?(?:name|property)=["\']' + re.escape(name) + r'["\'][^>]*?content=["\']([^"\']*)["\']'
    match = re.search(pattern, source, re.I)
    return html.unescape(match.group(1)) if match else ""

def extract(path):
    source = path.read_text(encoding="utf-8")
    block = re.search(r'<script\s+type=["\']application/json["\']\s+id=["\']aninextup-index["\']\s*>(.*?)</script>', source, re.S | re.I)
    if not block:
        return None
    try:
        data = json.loads(block.group(1))
    except json.JSONDecodeError:
        return None
    title = data.get("title") or meta(source, "og:title")
    if not title:
        return None
    published = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', source)
    modified = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})', source)
    date_value = published.group(1) if published else (modified.group(1) if modified else "")
    if not date_value:
        return None
    image = data.get("image") or meta(source, "og:image") or "/assets/images/anime-image-fallback.svg"
    if image.startswith("assets/"):
        image = "/" + image
    # Prefer optimized local editorial thumbnails only after they actually exist.
    local_thumb = ROOT / "assets" / "images" / "news" / (path.stem + ".webp")
    if local_thumb.is_file() and path.stem != "bleach-thousand-year-blood-war-graniph-collection-october-2026":
        image = "/assets/images/news/" + path.stem + ".webp"
    return dict(article="articles/" + path.stem, title=title, tag=data.get("tag") or "ANIME NEWS",
                description=data.get("description") or meta(source, "description"),
                image=image, published=date_value, updated=modified.group(1) if modified else date_value)

def publication_timestamp(path):
    # Git records the actual publication/integration time, including posts with the same visible datePublished.
    relative = path.relative_to(ROOT).as_posix()
    try:
        value = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct", "--", relative],
            cwd=ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
        return int(value) if value else 0
    except (OSError, ValueError, subprocess.CalledProcessError):
        return 0

def homepage_cards(items):
    cards = []
    for item in items:
        pinned = ' data-home-pinned="true"' if item["article"] in PINNED_ARTICLES else ""
        href = "/" + html.escape(item["article"], quote=True)
        image = html.escape(item["image"], quote=True)
        title = html.escape(item["title"], quote=True)
        tag = html.escape(item["tag"], quote=True)
        description = html.escape(item["description"], quote=True)
        cards.append(
            f'<a class="card story visual-card" href="{href}"{pinned}>'
            f'<img src="{image}" alt="{title}" loading="lazy">'
            f'<div class="visual-body"><span class="tag">{tag}</span>'
            f'<h3>{title}</h3><p>{description}</p>'
            f'<span class="more">READ UPDATE →</span></div></a>'
        )
    return "".join(cards)

def replace_cards(source, attribute, items):
    opening = re.search(r'<div\b(?=[^>]*\b' + re.escape(attribute) + r'\b)[^>]*>', source, re.I)
    if not opening:
        raise SystemExit("Could not find the homepage latest-news container")
    depth = 1
    content_start = opening.end()
    end = None
    for token in re.finditer(r'</?div\b[^>]*>', source[content_start:], re.I):
        if token.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                end = content_start + token.start()
                break
        else:
            depth += 1
    if end is None:
        raise SystemExit("Could not find the end of the homepage latest-news container")
    return source[:content_start] + homepage_cards(items) + source[end:]


def update_homepage(items):
    homepage = ROOT / "index.html"
    source = homepage.read_text(encoding="utf-8")
    source = replace_cards(source, "data-home-latest", items[:4])
    source = replace_cards(source, "data-home-more", items[4:24])
    homepage.write_text(source, encoding="utf-8")

def main():
    items = [item for path in ARTICLES.glob("*.html") if (item := extract(path))]
    items.sort(
        key=lambda item: (item["published"],
                          publication_timestamp(ARTICLES / (item["article"].split("/")[-1] + ".html")),
                          item["published"], item["article"]),
        reverse=True
    )
    pinned = [item for item in items if item["article"] in PINNED_ARTICLES]
    unpinned = [item for item in items if item["article"] not in PINNED_ARTICLES]
    # Keep the four freshest stories in the lead strip; pin substantially updated guides
    # immediately after them so the More Anime News pagination keeps them visible.
    latest = unpinned[:4] + pinned[:20] + unpinned[4:24-len(pinned[:20])]
    OUT.write_text(json.dumps({"generated":date.today().isoformat(),"items":latest}, ensure_ascii=False, separators=(",",":"))+"\n", encoding="utf-8")
    update_homepage(latest)
    print("Generated latest news:", len(items), "articles,", len(latest), "homepage cards")

if __name__ == "__main__":
    main()
