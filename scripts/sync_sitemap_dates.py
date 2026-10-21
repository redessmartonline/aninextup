#!/usr/bin/env python3
"""Synchronize article sitemap dates to authored editorial metadata, never today's date."""
from pathlib import Path
import re
from editorial_dates import article_lastmod

ROOT = Path(__file__).resolve().parents[1]

def sync_sitemap(raw, articles):
    changed = []
    def update(match):
        block = match[0]
        loc = re.search(r'<loc>https://aninextup.com/articles/([^<]+)</loc>', block)
        if not loc or loc[1] not in articles:
            return block
        day = article_lastmod(articles[loc[1]])
        if not day:
            return block
        new = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{day}</lastmod>', block)
        if new == block and '<lastmod>' not in block:
            new = block.replace('</url>', f'<lastmod>{day}</lastmod></url>')
        if new != block:
            changed.append(loc[1])
        return new
    return re.sub(r'<url\b[^>]*>.*?</url>', update, raw, flags=re.S), changed

def main():
    path = ROOT / 'sitemap.xml'
    pages = {p.stem: p.read_text(encoding='utf-8') for p in (ROOT/'articles').glob('*.html')}
    updated, changed = sync_sitemap(path.read_text(encoding='utf-8'), pages)
    path.write_text(updated, encoding='utf-8')
    print(f'Sitemap: {len(changed)} article dates synchronized to editorial metadata')

if __name__ == '__main__':
    main()
