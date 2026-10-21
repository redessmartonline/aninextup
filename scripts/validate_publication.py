#!/usr/bin/env python3
"""Fail closed on incomplete AniNextUp editorial proposals."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import subprocess
import sys
from validate_video_schema import video_schema_errors

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.images = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append((tag, d))
        if tag == "img": self.images.append(d)
        if tag == "a": self.links.append(d)

def validate(path):
    errors = []
    s = path.read_text(encoding="utf-8")
    errors.extend(video_schema_errors(s))
    dom = Audit()
    dom.feed(s)
    has = lambda tag, cls: any(t == tag and cls in a.get("class", "").split() for t, a in dom.tags)
    for tag, cls in (("header", "site-header"), ("article", "article"), ("div", "article-head"),
                     ("p", "lead"), ("p", "byline"), ("section", "release-summary"),
                     ("div", "prose"), ("section", "related-releases"),
                     ("div", "section-head"), ("div", "grid"), ("footer", "")):
        if cls and not has(tag, cls): errors.append("Missing " + tag + "." + cls)
    for required in ('KEEP WATCHING', 'Related releases', 'Release at a glance',
                     'rel="canonical"', 'og:image', 'twitter:image', 'og:title',
                     'og:description', 'twitter:card', 'BreadcrumbList',
                     'NewsArticle', 'aninextup-index', 'editorial-policy',
                     'googletagmanager.com/gtag/js?id=G-TRV5CF738D'):
        if required not in s: errors.append("Missing " + required)
    if not has("figure", "") and "<figure" not in s: errors.append("Missing official hero figure")
    cards = re.findall(r'<a\b[^>]*class="[^"]*related-card[^"]*"[^>]*>(.*?)</a>', s, re.S)
    if len(cards) != 2: errors.append("Expected exactly two related cards")
    for i, card in enumerate(cards):
        if 'related-card-image' not in card or 'related-card-copy' not in card or '<h3' not in card:
            errors.append(f"Related card {i+1} lacks image/copy/title")
    if not any(a.get("src") and a.get("alt") for a in dom.images):
        errors.append("No hero image with descriptive alt")
    match = re.search(r'<script type="application/json" id="aninextup-index">(.*?)</script>',s,re.S)
    if not match: errors.append("Missing index metadata")
    else:
        try:
            data=json.loads(match.group(1))
            if not data.get("image"): errors.append("Missing index image")
        except ValueError: errors.append("Invalid index JSON")
    if 'lite-trailer' in s:
        ids=re.findall(r'data-youtube="([A-Za-z0-9_-]{11})"',s)
        if not ids or 'VideoObject' not in s or 'youtube.com/watch?v=' not in s:
            errors.append("Trailer missing verified video markup/fallback")
    for tag, attrs in dom.tags:
        if tag == "script" and attrs.get("type") == "application/ld+json":
            pass
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
        try: json.loads(m.group(1))
        except ValueError: errors.append("Invalid JSON-LD")
    if len(s) < 4500: errors.append("Article appears abbreviated")
    return errors

def main():
    tracked=subprocess.check_output(["git","diff","--name-only","--","articles/"],text=True).splitlines()
    untracked=subprocess.check_output(["git","ls-files","--others","--exclude-standard","articles/"],text=True).splitlines()
    changed=sorted(set(tracked+untracked))
    if not changed:
        print("Quality gate: no article proposal to validate")
        return 0
    if len(changed)!=1:
        print("Quality gate: expected exactly one article",file=sys.stderr)
        return 1
    p=Path(changed[0])
    if p.suffix!=".html" or not p.is_file():
        print("Quality gate: invalid article path",file=sys.stderr)
        return 1
    errors=validate(p)
    if errors:
        for e in errors: print("BLOCKED:",e,file=sys.stderr)
        return 1
    print("PASS: article structure and editorial metadata:",p)
    return 0

if __name__=="__main__":
    sys.exit(main())
