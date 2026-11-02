#!/usr/bin/env python3
"""Compare Search Console Page Indexing drilldown exports with authored sitemap and HTML.

Usage: python scripts/audit_gsc_drilldowns.py discovered.csv crawled.csv
Accepts CSV files exported from Search Console (URL / Último rastreo).
This is a local technical audit, not a live Google indexing check.
"""
import csv
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urljoin

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://aninextup.com'

class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.canonicals = []
        self.noindex = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        rel = attrs.get('rel', '').lower().split()
        if tag == 'a' and attrs.get('href') and 'nofollow' not in rel:
            self.links.append(attrs['href'])
        if tag == 'link' and 'canonical' in rel:
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot'):
            self.noindex |= 'noindex' in attrs.get('content', '').lower().split(',')

def key(url):
    parsed = urlparse(urljoin(BASE, url))
    if parsed.netloc != 'aninextup.com':
        return None
    path = parsed.path.removesuffix('.html').rstrip('/')
    return path if path and path != '/index' else '/'

def load_export(path):
    with open(path, newline='', encoding='utf-8-sig') as file:
        rows = list(csv.DictReader(file))
    if not rows or 'URL' not in rows[0]:
        raise ValueError(f'{path}: expected a Search Console CSV with URL column')
    return rows

def audit(paths):
    sitemap = {e.text.strip() for e in ET.parse(ROOT / 'sitemap.xml').findall('.//{*}loc') if e.text}
    pages = {}
    for file in [*ROOT.glob('*.html'), *(ROOT / 'articles').glob('*.html')]:
        if file.name == '404.html':
            continue
        pages[key('/' + file.relative_to(ROOT).as_posix())] = Links(file.read_text(encoding='utf-8'))
    depth = {'/': 0}
    inbound = Counter()
    queue = deque(['/'])
    for source, page in pages.items():
        for href in page.links:
            dest = key(urljoin(BASE + source, href))
            if dest in pages:
                inbound[dest] += 1
    while queue:
        source = queue.popleft()
        for href in pages[source].links:
            dest = key(urljoin(BASE + source, href))
            if dest in pages and dest not in depth:
                depth[dest] = depth[source] + 1
                queue.append(dest)
    print('group,url,last_crawl,in_sitemap,local_html,self_canonical,noindex,html_inbound,click_depth,issues')
    for group, path in paths:
        for row in load_export(path):
            url = row['URL'].strip()
            k = key(url)
            page = pages.get(k)
            issues = []
            if k is None:
                issues.append('other-host')
            if url not in sitemap:
                issues.append('not-in-sitemap')
            if page is None:
                issues.append('missing-local-html')
            else:
                if page.canonicals != [BASE + k]:
                    issues.append('canonical-mismatch')
                if page.noindex:
                    issues.append('meta-noindex')
                if inbound[k] == 0:
                    issues.append('no-html-inbound')
                if k not in depth:
                    issues.append('unreachable-from-home')
            last = row.get('Último rastreo', '')
            if last.startswith('1969-'):
                last = ''
            values = [group, url, last, str(url in sitemap), str(page is not None),
                      str(bool(page and page.canonicals == [BASE + k])),
                      str(bool(page and page.noindex)), str(inbound[k]) if k else '0',
                      str(depth[k]) if k in depth else '', ';'.join(issues)]
            import io
            buf = io.StringIO()
            csv.writer(buf).writerow(values)
            print(buf.getvalue().rstrip())

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: audit_gsc_drilldowns.py discovered.csv crawled.csv')
    audit([('discovered', sys.argv[1]), ('crawled', sys.argv[2])])
