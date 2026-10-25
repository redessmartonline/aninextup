#!/usr/bin/env python3
"""Keep search visible in every header, and bust asset caches consistently."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
button = ('<button class="global-search-toggle" type="button" '
          'aria-label="Search articles" aria-expanded="false">'
          '<svg viewBox="0 0 24 24" aria-hidden="true">'
          '<circle cx="10.8" cy="10.8" r="6.8"></circle>'
          '<path d="m16 16 5 5"></path></svg>'
          '<span class="sr-only">Search</span></button>')
count = 0
for path in root.rglob("*.html"):
    if ".git" in path.parts:
        continue
    original = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'(href="(?:\.\./)*assets/style\.css)(?:\?[^"]*)?(")',
        lambda m: m.group(1) + '?v=20261024-independent-search' + m.group(2), original)
    updated = re.sub(
        r'(src="(?:\.\./)*assets/app\.js)(?:\?[^"]*)?(")',
        lambda m: m.group(1) + '?v=20261024-search-static' + m.group(2), updated)
    if '<header class="site-header">' in updated and 'global-search-toggle' not in updated.split('</header>',1)[0]:
        updated = updated.replace('</nav></header>', '</nav>' + button + '</header>', 1)
    if '<header class="site-header">' in updated and 'article-search.js' not in updated:\n        updated = updated.replace('</body>', '<script defer src="/assets/article-search.js?v=20261024-independent-search"></script></body>', 1)\n    if '<header class="site-header">' in updated and 'mobile-menu.js' not in updated:\n        updated = updated.replace('</body>', '<script defer src="/assets/mobile-menu.js?v=20261024-mobile-fix"></script></body>', 1)\n    if updated != original:
        path.write_text(updated, encoding="utf-8")
        count += 1
print(f"Updated {count} HTML pages")
