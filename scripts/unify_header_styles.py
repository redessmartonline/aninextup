#!/usr/bin/env python3
"""Give every HTML page the same cache-busted shared header stylesheet."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
version = '20261024-header-unified'
app_version = '20261024-search-restored'
count = 0
for path in root.rglob('*.html'):
    if '.git' in path.parts:
        continue
    original = path.read_text(encoding='utf-8')
    updated = re.sub(r'(href=["\\'](?:\\.\\./)*assets/style\\.css)(?:\\?[^"\\']*)?(["\\'])', lambda m: m.group(1) + '?v=' + version + m.group(2), original)
    updated = re.sub(r'(src=["\\'](?:\\.\\./)*assets/app\\.js)(?:\\?[^"\\']*)?(["\\'])', lambda m: m.group(1) + '?v=' + app_version + m.group(2), updated)
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        count += 1
print(f'Updated stylesheet references in {count} HTML files')
