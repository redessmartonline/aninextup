#!/usr/bin/env python3
"""Generate latest news from actual article metadata, without manually editing homepage."""
# Runs on article changes and may also be started manually from GitHub Actions.
import html, json, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
OUT = ROOT / "assets" / "latest-news.json"
SITEMAP = ROOT / "sitemap.xml"

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
    if local_thumb.is_file():
        image = "/assets/images/news/" + path.stem + ".webp"
    return dict(article="articles/" + path.stem, title=title, tag=data.get("tag") or "ANIME NEWS",
                description=data.get("description") or meta(source, "description"),
                image=image, published=date_value)

def main():
    items = [item for path in ARTICLES.glob("*.html") if (item := extract(path))]
    items.sort(key=lambda x: (x["published"], x["article"]), reverse=True)
    OUT.write_text(json.dumps({"generated":date.today().isoformat(),"items":items[:7]}, ensure_ascii=False, separators=(",",":"))+"\n", encoding="utf-8")
    if SITEMAP.exists():
        text = SITEMAP.read_text(encoding="utf-8")
        for item in items:
            url = "https://aninextup.com/" + item["article"]
            if url not in text:
                text = text.replace("</urlset>",f"  <url><loc>{url}</loc><lastmod>{item['published']}</lastmod></url>\n</urlset>")
        SITEMAP.write_text(text, encoding="utf-8")
    print("Generated latest news:", len(items), "articles,", len(items[:7]), "homepage cards")

if __name__ == "__main__":
    main()
