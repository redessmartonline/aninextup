#!/usr/bin/env python3
"""Refuse to deploy source HTML or an incomplete generated cover bundle.

Wrangler runs this custom build hook for both Cloudflare Workers Builds and
GitHub Actions. Only the prepared, audited GitHub build may reach production.
"""
from html.parser import HTMLParser
from pathlib import Path
import struct
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class ArticleCover(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hero = []
        self.social = {}
        self.srcsets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and 'article-original-cover' in attrs.get('class', '').split():
            self.hero.append(attrs.get('src', ''))
            self.srcsets.append(attrs.get('srcset', ''))
        key = attrs.get('property', attrs.get('name', ''))
        if tag == 'meta' and key in {'og:image', 'twitter:image'}:
            self.social[key] = attrs.get('content', '')


def bundle_errors(root):
    errors = []
    pages = sorted((root / 'articles').glob('*.html'))
    if not pages:
        return ['No published articles found.']
    for page in pages:
        article = ArticleCover()
        article.feed(page.read_text(encoding='utf-8'))
        if len(article.hero) != 1:
            errors.append(f'{page.name}: expected one generated article cover')
            continue
        path = urlsplit(article.hero[0]).path
        allowed = {f'/assets/article-covers/{page.stem}.png',
                   f'/assets/article-covers/{page.stem}-editorial.png'}
        if path not in allowed:
            errors.append(f'{page.name}: cover is not a prepared article asset')
            continue
        image = root / path.lstrip('/')
        try:
            with image.open('rb') as stream:
                header = stream.read(24)
            valid = (header[:8] == b'\x89PNG\r\n\x1a\n' and
                     header[12:16] == b'IHDR' and
                     struct.unpack('>II', header[16:24]) == (1200, 630))
        except (OSError, struct.error):
            valid = False
        if not valid:
            errors.append(f'{page.name}: missing or invalid 1200x630 cover {path}')
        if article.srcsets and article.srcsets[0]:
            candidate = article.srcsets[0].split()[0]
            expected = path.removesuffix('.png') + '.webp'
            try:
                header = (root / expected.lstrip('/')).read_bytes()[:12]
                valid_webp = header[:4] == b'RIFF' and header[8:12] == b'WEBP'
            except OSError:
                valid_webp = False
            if candidate != expected or not valid_webp:
                errors.append(f'{page.name}: missing or invalid lossless WebP cover')
        for key in ('og:image', 'twitter:image'):
            if article.social.get(key) != 'https://aninextup.com' + path:
                errors.append(f'{page.name}: {key} does not match the generated cover')
    return errors


def main():
    errors = bundle_errors(ROOT)
    if errors:
        print('DEPLOYMENT BLOCKED: the website has not been fully prepared.', file=sys.stderr)
        print('\n'.join(errors[:12]), file=sys.stderr)
        print('Publish through the Deploy AniNextUp Worker GitHub workflow. '
              'The current production version has not been replaced.', file=sys.stderr)
        return 1
    print(f'Production bundle ready: {len(list((ROOT / "articles").glob("*.html")))} '
          'articles with complete cover images and matching sharing metadata.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
