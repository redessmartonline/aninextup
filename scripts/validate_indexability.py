#!/usr/bin/env python3
"""Check authored indexing signals and crawlable HTML paths; not Google's index status."""
import fnmatch
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

BASE = 'https://aninextup.com'
ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonicals, self.directives = [], [], []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href') and 'nofollow' not in attrs.get('rel', '').lower().split():
            self.links.append(attrs['href'])
        if tag == 'link' and attrs.get('rel', '').lower() == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot'):
            self.directives.append(attrs.get('content', '').lower())
    @property
    def noindex(self):
        return any(re.search(r'\b(?:noindex|none)\b', value) for value in self.directives)

def path_key(path):
    path = path.removesuffix('.html').rstrip('/')
    return '/' if path in ('', '/index') else path

def headers_block_indexing(text, url):
    pattern = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line[0].isspace():
            pattern = re.sub(r':[A-Za-z]\w*', '*', line.strip())
        elif pattern and re.search(r'^\s*x-robots-tag\s*:.*\b(?:noindex|none)\b', line, re.I):
            if fnmatch.fnmatchcase(url, pattern) or fnmatch.fnmatchcase(urlparse(url).path, pattern):
                return True
    return False

def audit(root):
    errors = []
    robots = RobotFileParser()
    robots.parse((root/'robots.txt').read_text().splitlines())
    if BASE+'/sitemap.xml' not in (robots.site_maps() or []):
        errors.append('robots.txt does not declare the production sitemap')
    sitemap = ET.parse(root/'sitemap.xml').getroot()
    urls = [(node.text or '').strip() for node in sitemap.findall('{*}url/{*}loc')]
    if len(urls) != len(set(urls)):
        errors.append('Duplicate URLs in sitemap.xml')
    pages = {}
    for path in [*root.glob('*.html'), *(root/'articles').glob('*.html')]:
        if path.name != '404.html':
            pages[path_key('/'+path.relative_to(root).as_posix())] = Page(path.read_text())
    seen = {'/': 0}
    queue = deque(['/'])
    while queue:
        key = queue.popleft()
        page = pages[key]
        if page.noindex:
            continue
        for href in page.links:
            target = urlparse(urljoin(BASE+key, href))
            dest = path_key(target.path)
            if target.netloc == 'aninextup.com' and dest in pages and dest not in seen:
                seen[dest] = seen[key]+1
                queue.append(dest)
    headers = (root/'_headers').read_text()
    articles = {key: page for key,page in pages.items() if key.startswith('/articles/')}
    for key, page in articles.items():
        url = BASE+key
        if page.canonicals != [url]:
            errors.append(key+': expected exactly one self-referencing production canonical')
        if page.noindex or headers_block_indexing(headers, url):
            errors.append(key+': noindex directive applies')
        if not robots.can_fetch('Googlebot', url):
            errors.append(key+': robots.txt blocks Googlebot')
        if url not in urls:
            errors.append(key+': canonical URL missing from sitemap')
        if key not in seen:
            errors.append(key+': no crawlable HTML link path from homepage')
    return errors, len(articles), Counter(seen[key] for key in articles if key in seen)

if __name__ == '__main__':
    errors, count, depths = audit(ROOT)
    for error in errors:
        print('ERROR:', error)
    print(f'Indexability: {count} articles; {len(errors)} errors; HTML click depths {dict(sorted(depths.items()))}')
    print('Static checks only. Live HTTP responses, Google-selected canonicals and actual indexing require separate verification.')
    sys.exit(bool(errors))
