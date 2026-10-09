#!/usr/bin/env python3
"""Conservative, source-linked AniNextUp news publisher. No invented facts or AI keys."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = ("crunchyroll.com", "crunchyrollsvc.com", "tohoanimation.com", "anime.eiga.com")
FEEDS = [x.strip() for x in os.getenv("ANINEXTUP_OFFICIAL_FEEDS", "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss").split(",") if x.strip()]
MAX_AGE_HOURS = 72

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
        desc = clean(node.findtext("description"))
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
            desc = clean(node.findtext("a:summary", namespaces=ns))
            items.append((title, link, date, desc))
    return items

def date_of(raw):
    try:
        if "T" in raw:
            return dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
        return email.utils.parsedate_to_datetime(raw).astimezone(dt.timezone.utc)
    except (ValueError, TypeError, IndexError):
        return None

def main():
    now = dt.datetime.now(dt.timezone.utc)
    existing = {p.read_text(encoding="utf-8") for p in (ROOT / "articles").glob("*.html")}
    data = (ROOT / "assets/data.js").read_text(encoding="utf-8")
    candidates = []
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
            if len(title) < 22 or len(desc) < 90:
                stats["short_content"] += 1
                continue
            if any(link in page for page in existing):
                stats["duplicate"] += 1
                continue
            candidates.append((when, title, link, desc))
    print("Editorial eligibility diagnostics:", json.dumps(stats, sort_keys=True), "candidates=", len(candidates))
    if not candidates:
        print("Sin cambios en la página en esta ejecución: no eligible official announcements.")
        return
    when, title, link, desc = max(candidates, key=lambda c: c[0])
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
