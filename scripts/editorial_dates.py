"""Read editorial dates without treating release, video or maintenance dates as updates."""
import json
import re
from datetime import date

ARTICLE_TYPES = {'Article', 'NewsArticle', 'BlogPosting'}

def article_metadata(text):
    def walk(node):
        if isinstance(node, list):
            for child in node:
                yield from walk(child)
        elif isinstance(node, dict):
            types = node.get('@type', [])
            if ARTICLE_TYPES.intersection([types] if isinstance(types, str) else types):
                yield node
            if '@graph' in node:
                yield from walk(node['@graph'])
    for body in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.I | re.S):
        try:
            yield from walk(json.loads(body))
        except (ValueError, TypeError):
            continue  # The preflight separately reports malformed JSON-LD.

def iso_day(value):
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return None

def editorial_date_errors(text):
    errors = []
    panel = re.search(r'<p\b[^>]*class=["\'][^"\']*editorial-details[^"\']*["\'][^>]*>(.*?)</p>', text, re.S | re.I)
    visible = {}
    if panel:
        visible = dict(re.findall(r'(Updated|Published):\s*<time\b[^>]*datetime=["\'](\d{4}-\d{2}-\d{2})', panel[1], re.I))
        visible = {key.lower(): value for key, value in visible.items()}
    for item in article_metadata(text):
        published = iso_day(item.get('datePublished'))
        modified = iso_day(item.get('dateModified'))
        if item.get('datePublished') and not published:
            errors.append('invalid_article_publication_date')
        if item.get('dateModified') and not modified:
            errors.append('invalid_article_modified_date')
        if published and modified and modified < published:
            errors.append('article_modified_before_published')
        if 'updated' in visible and visible['updated'] != (modified or published):
            errors.append('visible_article_update_mismatch')
        if 'published' in visible and visible['published'] != published:
            errors.append('visible_article_publication_mismatch')
    return sorted(set(errors))

def article_lastmod(text):
    days = [iso_day(item.get('dateModified') or item.get('datePublished')) for item in article_metadata(text)]
    return max((day for day in days if day), default=None)
