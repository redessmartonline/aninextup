"""Ensure article navigation exists in HTML while preserving authored links."""
import datetime
import json
import re
from pathlib import Path
from auto_publish_news import related_release_section

ROOT = Path(__file__).resolve().parents[1]


def complete():
    data = (ROOT / 'assets/data.js').read_text(encoding='utf-8')
    changed = 0
    for path in sorted((ROOT / 'articles').glob('*.html')):
        original = page = path.read_text(encoding='utf-8')
        title = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
        if not title or '</article>' not in page:
            raise ValueError(f'{path.name}: missing article structure')
        if 'class="related-releases"' not in page:
            section = related_release_section(re.sub('<[^>]+>', '', title[1]), data, path.stem)
            page = page.replace('</article>', section + '</article>', 1)
        def headings(match):
            section = re.sub(r'(<span class="kicker">).*?(</span>)', r'\1KEEP WATCHING\2', match[0], count=1, flags=re.S)
            if 'KEEP WATCHING' not in section:
                section = re.sub(r'(<section[^>]*>)', r'\1<span class="kicker">KEEP WATCHING</span>', section, count=1)
            return re.sub(r'(<h2[^>]*>).*?(</h2>)', r'\1Related releases\2', section, count=1, flags=re.S)
        page = re.sub(r'<section class="related-releases"[^>]*>.*?</section>', headings, page, flags=re.S)
        if 'class="editorial-details"' not in page:
            dates = {}
            for raw in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', page, re.S):
                obj = json.loads(raw)
                if obj.get('@type') in ('Article', 'NewsArticle', 'BlogPosting'):
                    dates = obj
                    break
            stamp = dates.get('dateModified') or dates.get('datePublished')
            label = 'Updated' if dates.get('dateModified') else 'Published'
            date_html = ''
            if stamp:
                day = datetime.date.fromisoformat(stamp[:10])
                date_html = f'{label}: <time datetime="{day.isoformat()}">{day.strftime("%B %d, %Y")}</time> · '
            details = '<p class="editorial-details">' + date_html + '<a href="../editorial-policy">Sources, updates &amp; corrections</a> · <a href="../contact">Report an error</a></p>'
            page = page.replace('<section class="related-releases"', details + '<section class="related-releases"', 1)
        if page != original:
            path.write_text(page, encoding='utf-8')
            changed += 1
    print(f'Article navigation completed: {changed} pages.')


if __name__ == '__main__':
    complete()
