#!/usr/bin/env python3
"""Render a verified GA4 snapshot into static homepage cards; never query in-browser."""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def normalize(value):
    path = value.split('?', 1)[0].split('#', 1)[0].rstrip('/')
    return path[:-5] if path.endswith('.html') else path

def select(snapshot, root):
    start, end = date.fromisoformat(snapshot['dateFrom']), date.fromisoformat(snapshot['dateTo'])
    if (end-start).days != 29 or end >= date.fromisoformat(snapshot['checkedAt'][:10]):
        raise ValueError('Expected 30 complete days before the check date')
    if snapshot['source'] != 'GA4' or snapshot['property'] != '559369724' or snapshot['metric'] != 'screen_page_views':
        raise ValueError('Unexpected analytics source')
    totals = {}
    for row in snapshot['rows']:
        if row['hostname'] not in ('aninextup.com', 'www.aninextup.com'):
            continue
        path = normalize(row['page_path'])
        views = row['screen_page_views']
        if not isinstance(views, (int, float)) or isinstance(views, bool) or views < 0 or int(views) != views:
            raise ValueError('Invalid views')
        if not re.fullmatch(r'/articles/[a-z0-9-]+', path):
            continue
        file = root / (path.lstrip('/') + '.html')
        if not file.is_file():
            continue
        source = file.read_text(encoding='utf-8')
        if re.search(r'<meta[^>]+noindex', source, re.I):
            continue
        if 'https://aninextup.com'+path+'"' not in source:
            continue
        totals[path] = totals.get(path, 0) + int(views)
    ranked = sorted(totals, key=lambda path: (-totals[path], path))
    selected = []
    for path in ranked:
        if totals[path] <= 0:
            continue
        source = (root / (path.lstrip('/')+'.html')).read_text(encoding='utf-8')
        match = re.search(r'id="aninextup-index">(.*?)</script>', source, re.S)
        if not match:
            continue
        item = json.loads(match.group(1))
        image = item.get('image', '')
        if not item.get('title') or not image.startswith('/assets/') or not (root/image.lstrip('/')).is_file():
            continue
        selected.append(dict(url=path, title=item['title'], image=image, views=totals[path]))
        if len(selected) == 3:
            return selected
    raise ValueError('Fewer than three eligible articles with positive views')

def render(source, snapshot, selected):
    esc = lambda value: html.escape(str(value), quote=True)
    cards = ''.join(f'<a class="popular-news-card" href="{esc(i["url"])}"><img src="{esc(i["image"])}" alt="{esc(i["title"])}" loading="lazy"><div class="popular-news-copy"><span class="popular-news-rank">#{rank} · MOST VIEWED</span><h3>{esc(i["title"])}</h3><span class="more">READ ARTICLE →</span></div></a>' for rank, i in enumerate(selected, 1))
    section = '<section class="home-popular-news" aria-labelledby="popular-news-title"><div class="section-head"><div><span class="kicker">MOST VIEWED · LAST 30 COMPLETE DAYS</span><h2 id="popular-news-title">Popular News</h2></div></div><div class="home-popular-news-grid">'+cards+'</div></section>'
    result, count = re.subn(r'<section class="home-popular-news".*?</section>', lambda _:section, source, flags=re.S)
    if count != 1:
        raise ValueError('Expected one Popular News section')
    return result

def main():
    try:
        snapshot = json.loads((ROOT/'assets/popular-news.json').read_text())
        selected = select(snapshot, ROOT)
        target = ROOT/'index.html'
        before = target.read_text(encoding='utf-8')
        after = render(before, snapshot, selected)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Popular News preserved: '+str(exc))
        return
    if after != before:
        target.write_text(after, encoding='utf-8')
    print('Popular News verified:', ', '.join(i['url'] for i in selected))

if __name__ == '__main__':
    main()
