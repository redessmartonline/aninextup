#!/usr/bin/env python3
"""Conservative, source-linked AniNextUp news publisher. No invented facts or AI keys."""
import datetime as dt
import email.utils
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = ("crunchyroll.com", "crunchyrollsvc.com", "tohoanimation.com", "anime.eiga.com", "sonypictures.com")
FEEDS = [x.strip() for x in os.getenv("ANINEXTUP_OFFICIAL_FEEDS", "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss").split(",") if x.strip()]
MAX_AGE_HOURS = 72
MAX_ARTICLE_FETCHES = 8
# Additional official RSS/Atom feeds may be supplied through
# ANINEXTUP_OFFICIAL_FEEDS, comma-separated. Unknown/unapproved hosts are rejected.
# Sony Pictures is allowed for verified official releases; no unverified RSS URL
# is inserted into the defaults.

class OfficialArticleParser(HTMLParser):
    """Read editorial paragraphs and Article/NewsArticle JSON-LD conservatively."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.jsonld = []
        self.containers = []
        self.skip = []
        self.paragraph_depth = 0
        self.paragraph = []
        self.in_jsonld = False
        self.json_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.json_buffer = []
            return
        if tag in ("script", "style", "nav", "footer", "header", "aside", "form"):
            self.skip.append(tag)
        cls = " ".join((attrs.get("class", ""), attrs.get("id", ""))).lower()
        editorial = tag in ("article", "main") or bool(re.search(r"(?:^|[\s_-])(article-body|article-content|news-body|post-content|story-body|entry-content|rich-text)(?:$|[\s_-])", cls))
        self.containers.append((tag, editorial))
        if tag == "p" and not self.skip and any(v for _, v in self.containers[:-1]):
            self.paragraph_depth = 1
            self.paragraph = []
        elif self.paragraph_depth:
            self.paragraph_depth += 1

    def handle_data(self, data):
        if self.in_jsonld:
            self.json_buffer.append(data)
        elif self.paragraph_depth and not self.skip:
            self.paragraph.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_jsonld:
            self.jsonld.append("".join(self.json_buffer))
            self.in_jsonld = False
            self.json_buffer = []
        if self.paragraph_depth:
            self.paragraph_depth -= 1
            if self.paragraph_depth == 0 and tag == "p":
                text = clean(" ".join(self.paragraph))
                if len(text) >= 35:
                    self.parts.append(text)
                self.paragraph = []
        if self.skip and self.skip[-1] == tag:
            self.skip.pop()
        if self.containers and self.containers[-1][0] == tag:
            self.containers.pop()


def _article_bodies(value):
    if isinstance(value, list):
        for entry in value:
            yield from _article_bodies(entry)
    elif isinstance(value, dict):
        kinds = value.get("@type", [])
        if isinstance(kinds, str):
            kinds = [kinds]
        if any(str(k).rsplit("/", 1)[-1] in ("Article", "NewsArticle", "BlogPosting") for k in kinds):
            body = value.get("articleBody")
            if isinstance(body, str) and len(clean(body)) >= 180:
                yield clean(body)
        for key in ("@graph", "mainEntity"):
            if key in value:
                yield from _article_bodies(value[key])


def official_article_text(url):
    """Extract only attributable article text; no page-wide fallback."""
    if not host_allowed(url):
        return ""
    req = urllib.request.Request(url, headers={
        "User-Agent": "AniNextUpEditorial/1.0 (+https://aninextup.com/)",
        "Accept": "text/html",
    })
    with urllib.request.urlopen(req, timeout=12) as response:
        final_url = response.geturl()
        if not host_allowed(final_url):
            raise ValueError("Official article redirected to an unapproved host")
        content_type = response.headers.get("Content-Type", "").lower()
        print("Article HTTP:", response.status, "source_host:", urllib.parse.urlsplit(url).hostname,
              "final_host:", urllib.parse.urlsplit(final_url).hostname, "content_type:", content_type)
        if "text/html" not in content_type:
            print("Article rejection: non-HTML response")
            return ""
        body = response.read(500_001)
        if len(body) > 500_000:
            print("Article rejection: HTML exceeds size limit")
            return ""
        charset = response.headers.get_content_charset() or "utf-8"
    # Safe HTML diagnostics: structure only, never dump page content, cookies or headers.
    decoded = body.decode(charset, errors="replace")
    title_match = re.search(r"<title\\b[^>]*>(.*?)</title\\s*>", decoded, re.I | re.S)
    page_title = clean(title_match.group(1)) if title_match else "(missing)"
    page_title = re.sub(r"https?://\\S+|[\\w.+-]+@[\\w.-]+", "[redacted]", page_title)[:100]
    tag_counts = {
        tag: len(re.findall(r"<" + tag + r"\\b", decoded, re.I))
        for tag in ("html", "head", "body", "main", "article", "p", "script", "noscript")
    }
    jsonld_count = len(re.findall(
        r"<script\\b[^>]*type\\s*=\\s*['\\\"]application/ld\\+json['\\\"]",
        decoded, re.I
    ))
    print("HTML diagnostics:", json.dumps({
        "bytes": len(body),
        "title": page_title,
        "tags": tag_counts,
        "jsonld_script_tags": jsonld_count,
        "has_next_data": "__NEXT_DATA__" in decoded,
        "has_nuxt": "__NUXT__" in decoded,
        "has_cloudflare_challenge": "cf-challenge" in decoded.lower()
            or "challenge-platform" in decoded.lower(),
    }, ensure_ascii=False, sort_keys=True))
    if "cf-challenge" in decoded.lower() or "challenge-platform" in decoded.lower():
        print("Article blocked: Cloudflare challenge detected; skipping protected page")
        return ""
    parser = OfficialArticleParser()
    parser.feed(decoded)
    structured = []
    for raw in parser.jsonld:
        try:
            structured.extend(_article_bodies(json.loads(raw)))
        except (ValueError, TypeError):
            continue
    unique = list(dict.fromkeys(parser.parts))
    method = "jsonld-articleBody" if structured else "editorial-paragraphs"
    result = (structured[0] if structured else " ".join(unique))[:1200]
    print("Article extraction:", "method=", method, "jsonld_blocks=", len(parser.jsonld),
          "paragraphs=", len(unique), "characters=", len(result))
    if len(result) < 180:
        print("Article rejection: insufficient verified editorial text")
    return result


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AniNextUpEditorial/1.0 (+https://aninextup.com/)", "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read(2_000_000)

def host_allowed(url):
    u = urllib.parse.urlsplit(url)
    host = (u.hostname or "").lower()
    return u.scheme == "https" and any(host == h or host.endswith("." + h) for h in ALLOWED)

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", s or ""))).strip()

def items_from_feed(blob):
    root = ET.fromstring(blob)
    items = []
    for node in root.findall(".//item"):
        title = clean(node.findtext("title"))
        link = (node.findtext("link") or "").strip()
        if not link:
            guid = node.find("guid")
            if guid is not None and guid.attrib.get("isPermaLink", "true").lower() != "false":
                link = (guid.text or "").strip()
        date = (node.findtext("pubDate") or node.findtext("{http://purl.org/dc/elements/1.1/}date") or node.findtext("date") or "").strip()
        # Prefer full editorial text explicitly included by the feed publisher.
        # Do not synthesize or expand short snippets into unverified articles.
        desc_options = [
            node.findtext("{http://purl.org/rss/1.0/modules/content/}encoded"),
            node.findtext("description"),
            node.findtext("{http://search.yahoo.com/mrss/}description"),
        ]
        desc = max((clean(x) for x in desc_options if x), key=len, default="")
        items.append((title, link, date, desc))
    if not items:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for node in root.findall(".//a:entry", ns):
            title = clean(node.findtext("a:title", namespaces=ns))
            linknode = node.find("a:link[@rel='alternate']", ns)
            if linknode is None:
                linknode = node.find("a:link", ns)
            link = linknode.get("href", "") if linknode is not None else ""
            date = node.findtext("a:published", namespaces=ns) or node.findtext("a:updated", namespaces=ns) or ""
            desc_options = [
                node.findtext("a:content", namespaces=ns),
                node.findtext("a:summary", namespaces=ns),
            ]
            desc = max((clean(x) for x in desc_options if x), key=len, default="")
            items.append((title, link, date, desc))
    return items

def date_of(raw):
    """Parse RSS RFC 2822 dates and ISO 8601 dates without confusing GMT with ISO."""
    if not raw:
        return None
    raw = raw.strip()
    try:
        parsed = email.utils.parsedate_to_datetime(raw)
        if parsed is None:
            raise ValueError("Unrecognized RFC 2822 date")
    except (ValueError, TypeError, IndexError):
        try:
            parsed = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)

def opportunity_score(when, title, desc, now):
    """Conservative editorial heuristic; never claim measured demand or CTR."""
    age = (now - when).total_seconds() / 3600
    freshness = 20 if age <= 24 else 15 if age <= 48 else 10
    intent = 20 if re.search(r"\b(release|premiere|trailer|date|season|streaming|announced)\b", title, re.I) else 10
    ranking = 15 if len(title) >= 35 and len(title) <= 95 else 8
    value = 15 if len(desc) >= 180 else 10
    demand = 0  # No Search Console query data is available inside this workflow.
    return {"demand": demand, "freshness": freshness, "intent": intent, "ranking": ranking, "value": value}

def main():
    now = dt.datetime.now(dt.timezone.utc)
    existing = {p: p.read_text(encoding="utf-8") for p in (ROOT / "articles").glob("*.html")}
    data = (ROOT / "assets/data.js").read_text(encoding="utf-8")
    candidates = []
    article_fetches = 0
    stats = {"feeds":0,"entries":0,"missing_title":0,"invalid_url":0,"invalid_date":0,"outside_window":0,"short_content":0,"duplicate":0}
    for feed in FEEDS:
        if not host_allowed(feed):
            print("Skipping nonofficial feed:", feed)
            continue
        try:
            entries = items_from_feed(fetch(feed))
            stats["feeds"] += 1
            stats["entries"] += len(entries)
            print(f"Feed reachable: {feed}; entries={len(entries)}")
        except Exception as e:
            print("Feed unavailable; no publication:", type(e).__name__, str(e)[:200])
            continue
        for title, link, raw_date, desc in entries:
            when = date_of(raw_date)
            if not title:
                stats["missing_title"] += 1
                continue
            if not host_allowed(link):
                stats["invalid_url"] += 1
                if stats["invalid_url"] <= 3:
                    print("Rejected link host:", urllib.parse.urlsplit(link).hostname or "(missing)")
                continue
            if not when:
                stats["invalid_date"] += 1
                if stats["invalid_date"] <= 3:
                    print("Rejected publication date:", repr(raw_date[:80]))
                continue
            if not (dt.timedelta(0) <= now - when <= dt.timedelta(hours=MAX_AGE_HOURS)):
                stats["outside_window"] += 1
                continue
            # Without independent corroboration, only publish a transparent announcement
            # recap; never assert release dates, availability or plot facts from snippets.
            if len(title) < 22:
                stats["short_content"] += 1
                continue
            if len(desc) < 180 and article_fetches < MAX_ARTICLE_FETCHES:
                article_fetches += 1
                try:
                    expanded = official_article_text(link)
                    if len(expanded) >= 180:
                        desc = expanded
                        stats["expanded_from_official_article"] = stats.get("expanded_from_official_article", 0) + 1
                except Exception as exc:
                    stats["article_fetch_failed"] = stats.get("article_fetch_failed", 0) + 1
                    print("Official article unavailable:", type(exc).__name__, str(exc)[:100])
            if len(desc) < 180:
                stats["short_content"] += 1
                continue
            score_parts = opportunity_score(when, title, desc, now)
            score = sum(score_parts.values())
            if score < 60:
                stats.setdefault("below_threshold", 0)
                stats["below_threshold"] += 1
                continue
            matched = [p for p, page in existing.items() if html.escape(link, quote=True) in page or link in page]
            if len(matched) > 1:
                stats["duplicate"] += 1
                continue
            candidates.append((score, when, title, link, desc, score_parts, matched[0] if matched else None))
    print("Editorial eligibility diagnostics:", json.dumps(stats, sort_keys=True), "candidates=", len(candidates))
    if not candidates:
        print("Sin cambios en la página en esta ejecución: no eligible official announcements.")
        return
    # Prefer unpublished opportunities. Existing source URLs remain eligible
    # only when the official recap has genuinely changed.
    candidates.sort(key=lambda c: (c[6] is None, c[0], c[1]), reverse=True)
    for score, when, title, link, desc, parts, matched_path in candidates:
        print("Selected opportunity:", json.dumps({"score":score,"tier":"HIGH" if score >= 75 else "MEDIUM","components":parts,"source":link},sort_keys=True))
        if matched_path is not None:
            original = existing[matched_path]
            # Only touch pages generated by this publisher; preserve hand-edited articles.
            marker = '<h2>Official announcement</h2><p>'
            source = '<p>Source: <a href="' + html.escape(link, quote=True) + '"'
            if marker not in original or source not in original or 'id="aninextup-index"' not in original:
                print("Sin cambios: existing editorial article requires manual verification", matched_path.name)
                continue
            updated_desc = desc[:500].rsplit(" ", 1)[0] if len(desc) > 500 else desc
            begin = original.index(marker) + len(marker)
            finish = original.find('</p>', begin)
            if finish < 0:
                raise ValueError("Invalid generated article paragraph")
            old_desc = html.unescape(original[begin:finish])
            if clean(old_desc) == clean(updated_desc):
                print("Sin cambios: official source has no substantive update", matched_path.name)
                continue
            revised = original[:begin] + html.escape(updated_desc, quote=True) + original[finish:]
            revised, count = re.subn(r'("dateModified"\s*:\s*")[^"]+(")', lambda m: m.group(1) + now.date().isoformat() + m.group(2), revised, count=1)
            if count != 1:
                raise ValueError("Missing structured data dateModified")
            matched_path.write_text(revised, encoding="utf-8")
            print("Updated existing official recap", matched_path.relative_to(ROOT), "from", link)
            return
        # Avoid a second page for the same headline even if its source URL differs.
        normalized_title = clean(title).casefold()
        if any(
            clean(html.unescape(m.group(1))).casefold() == normalized_title
            for page in existing.values()
            for m in [re.search(r"<h1[^>]*>(.*?)</h1>", page, re.I | re.S)]
            if m is not None
        ):
            print("Sin cambios: same headline already published", title)
            continue
        # This candidate is new and meets the editorial threshold.
        break
    else:
        print("Sin cambios: all eligible official announcements already covered.")
        return
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:65].strip("-")
    slug += "-" + hashlib.sha256(link.encode()).hexdigest()[:8]
    dest = ROOT / "articles" / (slug + ".html")
    if dest.exists() or ('article:"articles/' + dest.name + '"') in data:
        print("Sin cambios: existing entry")
        return
    title_e = html.escape(title, quote=True)
    desc = desc[:500].rsplit(" ", 1)[0] if len(desc) > 500 else desc
    desc_e = html.escape(desc, quote=True)
    link_e = html.escape(link, quote=True)
    canonical = "https://aninextup.com/articles/" + dest.name
    today = now.date().isoformat()
    headline = title + " — Official Announcement"
    # Do not publish misleading HIGH/MEDIUM scoring based on unmeasured search demand.
    # Only a source-linked recap; no inferred facts.
    summary = f"Official announcement published by Crunchyroll on {when.date().isoformat()}. Read the original announcement for full details."
    structured = {"@context":"https://schema.org","@type":"Article","headline":headline,"description":summary,"datePublished":today,"dateModified":today,"mainEntityOfPage":canonical,"author":{"@type":"Organization","name":"AniNextUp Editorial Team"},"publisher":{"@type":"Organization","name":"AniNextUp"}}
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://aninextup.com/"},{"@type":"ListItem","position":2,"name":title,"item":canonical}]}
    index = {"kind":"guide","image":"assets/favicon.svg","title":title,"tag":"OFFICIAL NEWS","description":summary}
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title_e} — AniNextUp</title><meta name="description" content="{html.escape(summary,quote=True)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}"><meta property="og:type" content="article"><meta property="og:title" content="{title_e}"><meta property="og:description" content="{html.escape(summary,quote=True)}"><meta property="og:url" content="{canonical}"><link rel="stylesheet" href="../assets/style.css"><script type="application/ld+json">{json.dumps(structured,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb,separators=(',',':'))}</script><script type="application/json" id="aninextup-index">{json.dumps(index,separators=(',',':'))}</script></head><body><header class="site-header"><a class="brand" href="../index.html">ANI<span>NEXTUP</span></a><button class="menu">☰</button><nav><a href="../today.html">TODAY</a><a href="../this-week.html">THIS WEEK</a><a href="../calendar.html">CALENDAR</a><a href="../where-to-watch.html">WHERE TO WATCH</a><a href="../news.html">NEWS</a></nav></header><main><article class="article"><div class="article-head"><span class="kicker">OFFICIAL NEWS · {today}</span><h1>{title_e}</h1><p class="lead">{html.escape(summary)}</p><p class="byline">By <a href="../about.html">AniNextUp Editorial Team</a></p></div><div class="prose"><h2>Official announcement</h2><p>{desc_e}</p><p>Source: <a href="{link_e}" rel="noopener noreferrer">Read the original announcement on Crunchyroll</a>. Details may change; consult the original announcement for updates.</p><p>Explore the <a href="../calendar.html">anime release calendar</a> and <a href="../news.html">latest news</a>.</p></div></article></main><footer><b>ANINEXTUP</b><small>Anime releases, streaming guides, calendars and news.</small></footer><script src="../assets/app.js"></script></body></html>'''
    dest.write_text(page, encoding="utf-8")
    print("Created", dest.relative_to(ROOT), "from", link)

if __name__ == "__main__":
    main()
