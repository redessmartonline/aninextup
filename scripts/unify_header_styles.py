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
    updated = re.sub(r'(href="(?:\\.\\./)*assets/style\\.css)(?:\\?[^"]*)?(")', r'\\g<1>?v=20261024-header-unified\\2', original)
    updated = re.sub(r'(src="(?:\\.\\./)*assets/app\\.js)(?:\\?[^"]*)?(")', r'\\g<1>?v=20261024-search-restored\\2', updated)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        count += 1
print(f"Updated stylesheet and app references in {count} HTML files")
