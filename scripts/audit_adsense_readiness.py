#!/usr/bin/env python3
"""Read-only AdSense readiness audit. Never alters articles or publishes ads."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"404.html"}
REQUIRED = ["index.html", "about.html", "contact.html", "privacy.html", "terms.html", "editorial-policy.html", "ads.txt", "robots.txt", "sitemap.xml"]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.text = []
        self.title = ""
        self.in_title = False
        self.skip = 0
        self.canonical = []
        self.description = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            self.images.append((a.get("src", ""), a.get("alt", "")))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href", ""))
        if tag == "meta" and a.get("name", "").lower() == "description":
            self.description.append(a.get("content", ""))
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "title":
            self.in_title = False
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if not self.skip and data.strip():
            self.text.append(data.strip())

def audit():
    issues = []
    warnings = []
    pages = {}
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            issues.append(f"MISSING {name}")
    for path in sorted(ROOT.rglob("*.html")):
        if path.name in EXCLUDE or ".git" in path.parts:
            continue
        p = Page()
        try:
            p.feed(path.read_text(encoding="utf-8"))
        except (UnicodeError, ValueError) as exc:
            issues.append(f"PARSE {path.relative_to(ROOT)}: {exc}")
            continue
        rel = path.relative_to(ROOT).as_posix()
        pages[rel] = p
        if not p.title.strip():
            issues.append(f"NO TITLE {rel}")
        if not p.description:
            warnings.append(f"NO META DESCRIPTION {rel}")
        if not p.canonical:
            warnings.append(f"NO CANONICAL {rel}")
        for src, alt in p.images:
            if not alt.strip():
                warnings.append(f"IMAGE WITHOUT ALT {rel}: {src[:80]}")
            if not src or src.startswith(("data:", "http:", "https:", "//")):
                continue
            image_path = urllib.parse.unquote(urllib.parse.urlsplit(src).path)
            local = ((ROOT / image_path.lstrip("/")) if image_path.startswith("/") else (path.parent / image_path)).resolve()
            if local.is_relative_to(ROOT) and not local.is_file():
                issues.append(f"BROKEN IMAGE {rel}: {src}")
        for href in p.links:
            if href.startswith(("mailto:", "tel:", "#", "javascript:", "http:", "https:", "//")):
                continue
            url = urllib.parse.urlsplit(href)
            dest = (ROOT / url.path.lstrip("/")) if href.startswith("/") else (path.parent / url.path)
            dest = dest.resolve()
            if not dest.is_relative_to(ROOT):
                issues.append(f"LINK ESCAPES ROOT {rel}: {href}")
                continue
            if dest.is_file() or dest.is_dir() or dest.with_suffix(".html").is_file():
                continue
            issues.append(f"BROKEN INTERNAL LINK {rel}: {href}")
        if rel.startswith("articles/"):
            prose = re.sub(r"\s+", " ", " ".join(p.text))
            if len(prose.split()) < 220:
                warnings.append(f"THIN ARTICLE REVIEW {rel}: {len(prose.split())} words")
            if not any("http" in href and "aninextup.com" not in href for href in p.links):
                warnings.append(f"ARTICLE WITHOUT EXTERNAL SOURCE {rel}")
    for title, count in Counter(p.title.strip().lower() for p in pages.values()).items():
        if title and count > 1:
            warnings.append(f"DUPLICATE TITLE {count}x: {title}")
    sitemap = ROOT / "sitemap.xml"
    if sitemap.is_file():
        try:
            tree = ET.parse(sitemap)
            locs = [x.text or "" for x in tree.findall(".//{*}loc")]
            for loc in locs:
                u = urllib.parse.urlsplit(loc)
                if u.hostname != "aninextup.com":
                    warnings.append(f"NONCANONICAL SITEMAP URL {loc}")
                elif not (ROOT / u.path.lstrip("/")).is_file() and not (ROOT / (u.path.lstrip("/") + ".html")).is_file() and u.path != "/":
                    issues.append(f"SITEMAP URL WITHOUT FILE {loc}")
        except ET.ParseError as exc:
            issues.append(f"INVALID SITEMAP {exc}")
    ads = ROOT / "ads.txt"
    if ads.is_file() and not re.search(r"^google\.com,\s*pub-\d+,\s*DIRECT,\s*f08c47fec0942fa0\s*$", ads.read_text(), re.M):
        warnings.append("ADS.TXT: verify authorized publisher record")
    print(f"Audited {len(pages)} HTML pages")
    print(f"Errors: {len(issues)}; editorial/manual warnings: {len(warnings)}")
    for issue in issues[:150]:
        print("ERROR:", issue)
    for warning in warnings[:150]:
        print("REVIEW:", warning)
    print("NOTE: Account approval, live HTTP status, factual accuracy, copyright and ad consent require separate verification.")
    return 1 if issues else 0

if __name__ == "__main__":
    sys.exit(audit())
