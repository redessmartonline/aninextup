#!/usr/bin/env python3
"""Keep stylesheet and app-script cache versions consistent on all HTML pages."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
count = 0
for path in root.rglob("*.html"):
    if ".git" in path.parts:
        continue
    original = path.read_text(encoding="utf-8")
    updated = re.sub(r'(href="(?:\\.\\./)*assets/style\\.css)(?:\\?[^"]*)?(")', lambda m: m.group(1) + '?v=20261024-header-unified' + m.group(2), original)
    updated = re.sub(r'(src="(?:\\.\\./)*assets/app\\.js)(?:\\?[^"]*)?(")', lambda m: m.group(1) + '?v=20261024-articles-only' + m.group(2), updated)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        count += 1
print(f"Updated stylesheet and app references in {count} HTML files")
