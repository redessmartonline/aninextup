#!/usr/bin/env python3
"""Ensure every existing Related releases section has exactly three cards."""
import re
import html
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
    plain_title = html.unescape(re.sub(r'<[^>]+>', '', title.group(1)))
    replacement = related_release_section(plain_title, data, path.stem)
    if len(re.findall(r'class="mini related-card"', replacement)) != 3:
        raise RuntimeError(f"{path.name}: expected exactly three related cards")
    source = source[:match.start()] + replacement + source[match.end():]
    # Invalidate old cached article runtime so every article loads the 3-card logic.
    source = re.sub(r'(src="../assets/app[.]js)(?:[?]v=[^"]*)?(")', r'\g<1>?v=20261024-all-related-three\2', source)
    if source != path.read_text(encoding="utf-8"):
        path.write_text(source, encoding="utf-8")
        changed += 1
print(f"Updated {changed} articles with exactly three related releases")
