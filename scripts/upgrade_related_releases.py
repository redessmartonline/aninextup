#!/usr/bin/env python3
"""Rebuild legacy two-card Related releases sections with three valid cards."""
import re
from pathlib import Path
from auto_publish_news import related_release_section

ROOT = Path(__file__).resolve().parents[1]
data = (ROOT / "assets/data.js").read_text(encoding="utf-8")
changed = 0
for path in sorted((ROOT / "articles").glob("*.html")):
    source = path.read_text(encoding="utf-8")
    match = re.search(r'<section class="related-releases"[^>]*>.*?<h2[^>]*>Related releases</h2>.*?</section>', source, re.S)
    if not match:
        continue
    title = re.search(r'<h1[^>]*>(.*?)</h1>', source, re.S)
    if not title:
        continue
    plain_title = re.sub(r'<[^>]+>', '', title.group(1))
    replacement = related_release_section(plain_title, data, path.stem)
    if replacement != match.group(0):
        path.write_text(source[:match.start()] + replacement + source[match.end():], encoding="utf-8")
        changed += 1
print(f"Updated {changed} Related releases sections to three cards")
