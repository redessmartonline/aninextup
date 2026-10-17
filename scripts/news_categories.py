"""Conservative classification for AniNextUp's four News subcategories."""
import html
import json
import re

CATEGORIES = {"new-anime", "returning-series", "trailers-cast", "release-news"}

def classify_news_category(source, kind="guide"):
    """Return a News category only for clearly relevant anime-industry news."""
    if isinstance(source, dict):
        meta = source
        title = str(meta.get("title", ""))
        description = str(meta.get("description", ""))
        body = str(meta.get("article", ""))
    else:
        text = str(source or "")
        block = re.search(r'<script[^>]+id=["\']aninextup-index["\'][^>]*>(.*?)</script>', text, re.I | re.S)
        meta = {}
        if block:
            try:
                meta = json.loads(html.unescape(block.group(1)))
            except (ValueError, TypeError):
                meta = {}
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
        title = html.unescape(re.sub(r"<[^>]+>", " ", title_match.group(1))).strip() if title_match else str(meta.get("title", ""))
        description_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.I | re.S)
        description = html.unescape(description_match.group(1)) if description_match else str(meta.get("description", ""))
        body = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
        body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    explicit = meta.get("newsCategory")
    if explicit in CATEGORIES:
        return explicit
    headline = re.sub(r"\s+", " ", title + " " + description).casefold()
    full_text = re.sub(r"\s+", " ", title + " " + description + " " + body).casefold()
    if re.search(r"\b(roblox|redeem(?:ing)?|game codes?|codes? at a glance|walkthrough|game guide|gameplay)\b", headline):
        return None
    if kind == "anime" and not re.search(r"\b(announc|confirmed|reveals?|trailer|teaser|cast|pv|promotional video|news)\b", headline):
        return None
    if not re.search(r"\b(anime|animated film|animation|manga adaptation|anime adaptation|tv anime|anime series)\b", full_text):
        return None
    sequel = re.search(r"\b(season\s*(?:2|3|4|ii|iii|iv)|second season|third season|fourth season|sequel|cour\s*2|part\s*2|returns? for|returning series)\b", headline)
    first_adaptation = re.search(r"\b(anime adaptation|tv anime|anime series)\b.{0,55}\b(announc|confirm|adapt|greenlit|gets|receives|production)\w*|\b(?:announc|confirm|greenlit|gets|receives)\w*.{0,45}\b(?:anime adaptation|tv anime|anime series)\b", headline)
    if sequel:
        return "returning-series"
    if first_adaptation or re.search(r"\banime (?:announc|confirm)\w*\b", headline):
        return "new-anime"
    if re.search(r"\b(trailer|teaser|promo(?:tional)? video|pv|voice cast|cast (?:reveal|announc)|new cast)\b", headline):
        return "trailers-cast"
    if re.search(r"\b(release date|premiere|premieres|streaming (?:lineup|date|release)|launch(?:es)?|opens in|arrives on|merchandise|collection launch|broadcast date)\b", headline):
        return "release-news"
    return None
