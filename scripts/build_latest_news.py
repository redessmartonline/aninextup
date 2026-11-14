#!/usr/bin/env python3
"""Generate latest news from actual article metadata, without manually editing homepage."""
# Runs on article changes and may also be started manually from GitHub Actions.
# Full Git history is required to sort same-day articles by publication commit time.
import html, json, re, subprocess
from datetime import date
from pathlib import Path

if __package__:
    from .editorial_dates import article_metadata, iso_day
else:
    from editorial_dates import article_metadata, iso_day

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
OUT = ROOT / "assets" / "latest-news.json"

def meta(source, name):
    pattern = r'<meta\s+[^>]*?(?:name|property)=["\']' + re.escape(name) + r'["\'][^>]*?content=["\']([^"\']*)["\']'
    match = re.search(pattern, source, re.I)
    return html.unescape(match.group(1)) if match else ""

def extract(path):
    source = path.read_text(encoding="utf-8")
    block = re.search(r'<script\s+type=["\']application/json["\']\s+id=["\']aninextup-index["\']\s*>(.*?)</script>', source, re.S | re.I)
    # Standard article metadata is sufficient; legacy publications may not have
    # the optional AniNextUp index block.
    if "noindex" in meta(source, "robots").lower():
        return None
    data = {}
    if block:
        try:
            data = json.loads(block.group(1))
        except json.JSONDecodeError:
            pass
    if not data and not any('"' + kind + '"' in source for kind in ("NewsArticle", "Article", "BlogPosting")):
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
    # Use the original addition time; later edits must not promote an older article.
    relative = path.relative_to(ROOT).as_posix()
    try:
        value = subprocess.check_output(
            ["git", "log", "-1", "--diff-filter=A", "--format=%ct", "--", relative],
            cwd=ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
        return int(value) if value else 0
    except (OSError, ValueError, subprocess.CalledProcessError):
        return 0

def updated_guide(path, item):
    source = path.read_text(encoding="utf-8")
    if not re.search(r'<section\b[^>]*\bclass=["\'][^"\']*\brelease-summary\b', source, re.I):
        return None
    for metadata in article_metadata(source):
        published = iso_day(metadata.get("datePublished"))
        updated = iso_day(metadata.get("dateModified"))
        if published and updated and updated > published:
            return dict(item, title=meta(source, "og:title") or item["title"],
                        updated=updated, tag="UPDATED VIEWING GUIDE")
    return None

def homepage_cards(items, link_label="READ UPDATE", show_lead=False):
    cards = []
    for position, item in enumerate(items):
        href = "/" + html.escape(item["article"], quote=True)
        title = html.escape(item["title"], quote=True)
        tag = html.escape(item["tag"], quote=True)
        description = html.escape(item["description"], quote=True)
        artwork = ('<img src="/assets/images/anime-image-fallback.svg" alt="" width="640" height="360">'
                   if show_lead and position == 0 else "")
        cards.append(
            f'<a class="card story visual-card" href="{href}">' +
            artwork +
            f'<div class="visual-body"><span class="tag">{tag}</span>'
            f'<h3>{title}</h3><p>{description}</p>'
            f'<span class="more">{link_label} →</span></div></a>'
        )
    return "".join(cards)

def replace_cards(source, attribute, items, link_label="READ UPDATE", show_lead=False):
    opening = re.search(r'<div\b(?=[^>]*\b' + re.escape(attribute) + r'\b)[^>]*>', source, re.I)
    if not opening:
        raise SystemExit(f"Could not find the homepage container {attribute}")
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
        raise SystemExit(f"Could not find the end of the homepage container {attribute}")
    return source[:content_start] + homepage_cards(items, link_label, show_lead) + source[end:]


def update_homepage(items, guides):
    homepage = ROOT / "index.html"
    source = homepage.read_text(encoding="utf-8")
    source = replace_cards(source, "data-home-latest", items[:4], show_lead=True)
    source = replace_cards(source, "data-home-more", items[4:])
    source = replace_cards(source, "data-home-updated-guides", guides[:6], "READ GUIDE")
    homepage.write_text(source, encoding="utf-8")

def main():
    items = [item for path in ARTICLES.glob("*.html") if (item := extract(path))]
    items.sort(
        key=lambda item: (item["published"],
                          publication_timestamp(ARTICLES / (item["article"].split("/")[-1] + ".html")),
                          item["article"]),
        reverse=True
    )
    # Publication order is shared by the lead strip and the complete archive.
    # Edits and previous editorial pins do not promote an older publication.
    latest = items
    OUT.write_text(json.dumps({"generated":date.today().isoformat(),"items":latest}, ensure_ascii=False, separators=(",",":"))+"\n", encoding="utf-8")
    guides = [guide for item in latest
              if (guide := updated_guide(ROOT / (item["article"] + ".html"), item))]
    guides.sort(key=lambda guide: guide["updated"], reverse=True)
    update_homepage(latest, guides)
    print("Generated latest news:", len(items), "articles,", len(latest), "homepage cards")

if __name__ == "__main__":
    main()
