"""Render consistent related-article sections from the published article catalog."""
import json
import re
from html import escape, unescape
from pathlib import Path

SECTION = re.compile(r'<section\b(?=[^>]*\bclass="[^"]*\brelated-releases\b)[^>]*>.*?</section>', re.S)
INDEX = re.compile(r'<script\b[^>]*\bid="aninextup-index"[^>]*>(.*?)</script>', re.S)
DESCRIPTION = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"')
STOP = set(
    "anime season release date dates where watch official guide guides latest news original "
    "update updates confirmed schedule streaming trailer teaser episodes first part new returning "
    "series announced announces cast story movie film debut anime tv the and for with this what "
    "from into english dub free online after before your chapter channels reveals netflix "
    "crunchyroll hidive prime video january february march april june july august september "
    "october november december spring summer fall winter netflix manga premiere time".split()
)
# Complement the editorial genre catalog with subjects that span different article types.
TOPICS = (
    ("roblox", r"roblox|anime.crusaders.x|anime-(?:expeditions|mysterious|vs-anime)-codes"),
    ("pokemon", r"pok(?:é|e|-)mon"),
    ("zombies", r"zombies?"),
    ("horror", r"zombies?|horror|vampire|grotesqqque"),
    ("sports", r"ace.of.diamond|aoashi|blue.box|medalist|the.boxer"),
    ("mecha", r"dandivine|dark.machine|yamato|gundam|votoms|rakuen.tsuihou|expelled.from.paradise"),
    ("music", r"aikatsu|love.live|bocchi|maebashi.witches|kinioto"),
    ("release-calendar", r"anime-releasing-|anime-calendar|new-anime-20"),
)
FRANCHISES = ("apothecary-diaries", "firefly-wedding", "one-piece", "bleach", "sasaki-and-peeps",
              "naruto", "pokemon-horizons", "pok-mon-horizons")


def read_article(page):
    source = page.read_text(encoding="utf-8")
    block = INDEX.search(source)
    meta = json.loads(block[1]) if block else {}
    heading = re.search(r'<h1\b[^>]*>(.*?)</h1>', source, re.S)
    title = meta.get("title") or unescape(re.sub(r"<[^>]*>", "", heading[1]))
    description = DESCRIPTION.search(source)
    summary = meta.get("description") or (unescape(description[1]) if description else "")
    if not summary.strip():
        raise ValueError(f"Missing description for related article: {page}")
    key = page.stem
    topics = {topic for topic, pattern in TOPICS if re.search(pattern, key, re.I)}
    series = {name for name in FRANCHISES if name in key}
    if "pokemon" in topics:
        series.add("pokemon")
    terms = {word for word in re.findall(r"[a-z]{3,}", title.lower()) if word not in STOP}
    section = SECTION.search(source)
    previous = set(re.findall(r'href="(?:\./|/articles/)?([a-z0-9-]+)(?:\.html)?"', section[0])) if section else set()
    return {"source": source, "title": title, "summary": summary, "terms": terms, "topics": topics,
            "series": series, "previous": previous, "platforms": set(re.findall(
                r"netflix|crunchyroll|hidive|prime video|roblox", str(meta.get("platform", "")).lower())),
            "category": meta.get("newsCategory")}


def render_related_releases(pages, covers, genre_path):
    genres = json.loads(genre_path.read_text(encoding="utf-8"))
    catalog = {page.stem: read_article(page) for page in pages}
    for page in pages:
        slug = page.stem
        item = catalog[slug]
        def rank(candidate):
            other = catalog[candidate]
            shared_genres = set(genres.get(slug, [])) & set(genres.get(candidate, []))
            shared_terms = item["terms"] & other["terms"]
            return (
                -len(item["series"] & other["series"]),
                -len(item["topics"] & other["topics"]),
                -int(len(shared_terms) >= 2),
                -len(shared_genres),
                -len(item["platforms"] & other["platforms"]),
                -len(shared_terms),
                -int(candidate in item["previous"]),
                -int(bool(item["category"] and item["category"] == other["category"])),
                candidate,
            )
        recommendations = sorted(catalog.keys() - {slug}, key=rank)[:3]
        cards = []
        for candidate in recommendations:
            related = catalog[candidate]
            cover, height = covers[candidate]
            cards.append(
                f'<a class="mini related-card" href="/articles/{candidate}">'
                f'<img class="related-card-image" src="/assets/article-covers/{cover}" '
                f'width="1200" height="{height}" alt="" loading="lazy" decoding="async">'
                '<div class="related-card-copy">'
                f'<h3>{escape(related["title"])}</h3><p>{escape(related["summary"])}</p>'
                '<span>Read the guide →</span></div></a>'
            )
        section = (
            '<section class="related-releases" aria-labelledby="related-releases-heading">'
            '<div class="section-head"><div><span class="kicker">KEEP WATCHING</span>'
            '<h2 id="related-releases-heading">Related releases</h2></div></div>'
            '<div class="grid three">' + "".join(cards) + '</div></section>'
        )
        source, count = SECTION.subn(lambda _: section, item["source"])
        if count == 0:
            source = source.replace("</article>", section + "</article>", 1)
        if count > 1 or section not in source:
            raise ValueError(f"Unable to build exactly one Related releases section: {page}")
        page.write_text(source, encoding="utf-8")
