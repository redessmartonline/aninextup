"""Ensure article navigation exists in HTML while preserving authored links."""
import datetime
import json
import re
import html
from pathlib import Path
from auto_publish_news import related_release_section

ROOT = Path(__file__).resolve().parents[1]

RELATED_STORY_OVERRIDES = {
    'one-piece-elbaph-arc-english-dub-october-2026': [
        ('reincarnated-as-a-sword-season-2-english-dub-release-date', 'DUB RELEASE', 'Reincarnated as a Sword Season 2 English Dub Starts October 21 on HIDIVE', 'https://img.youtube.com/vi/Yt364dCCxIE/maxresdefault.jpg'),
        ('the-one-piece-netflix-february-2027', 'NETFLIX ANIME', 'THE ONE PIECE: February 2027 Release Date, Episodes & Trailer', 'https://img.youtube.com/vi/3Gmo0EXHyKg/maxresdefault.jpg'),
        ('bleach-thousand-year-blood-war-the-last-pv-episodes-49-50', 'OFFICIAL TRAILER NEWS', 'BLEACH: Thousand-Year Blood War Releases “THE LAST PV”', 'https://www.aniplex.co.jp/news/detail/SYS/CONTENTS/3bf96511-2b17-4fe2-8d7d-13fd99bc8a0e/w707'),
    ],
    'reincarnated-as-a-sword-season-2-english-dub-release-date': [
        ('one-piece-elbaph-arc-english-dub-october-2026', 'DUB RELEASE', 'ONE PIECE: Elbaph Arc English Dub Starts October 20 on Crunchyroll', 'https://img.youtube.com/vi/YnczpEoeaDM/maxresdefault.jpg'),
        ('berserk-of-gluttony-season-2', 'RETURNING SERIES', 'Berserk of Gluttony Season 2 Confirmed for 2027: New Trailer and Streaming Details', 'https://i.ytimg.com/vi/BVz1EyrHILk/maxresdefault.jpg'),
        ('iceblade-sorcerer-ii', 'FALL 2026 RELEASE', 'The Iceblade Sorcerer Shall Rule the World II', 'https://hyouken-anime.com/wp/wp-content/themes/hyouken-theme/images/kv1.webp'),
    ],
}

for article_slug, cards in RELATED_STORY_OVERRIDES.items():
    targets = [card[0] for card in cards]
    if len(targets) != 3 or len(set(targets)) != 3 or article_slug in targets:
        raise ValueError(f'{article_slug}: related stories must be three unique articles excluding itself')


def related_stories_section(cards):
    links = []
    for slug, label, title, image in cards:
        safe_slug = html.escape(slug, quote=True)
        safe_label = html.escape(label)
        safe_title = html.escape(title, quote=True)
        safe_image = html.escape(image, quote=True)
        links.append(
            f'<a class="mini related-card" href="{safe_slug}">'
            f'<img class="related-card-image" src="{safe_image}" alt="{safe_title}" '
            'width="160" height="90" loading="lazy" decoding="async">'
            f'<div class="related-card-copy"><b>{safe_label}</b><h3>{html.escape(title)}</h3>'
            '<span>Read story →</span></div></a>'
        )
    return (
        '<section class="related-releases" aria-labelledby="related-releases-heading">'
        '<div class="section-head"><div><span class="kicker">MORE ANIME NEWS</span>'
        '<h2 id="related-releases-heading">Related stories</h2></div></div>'
        '<div class="grid three">' + ''.join(links) + '</div></section>'
    )


def complete():
    data = (ROOT / 'assets/data.js').read_text(encoding='utf-8')
    changed = 0
    for path in sorted((ROOT / 'articles').glob('*.html')):
        original = page = path.read_text(encoding='utf-8')
        title = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
        if not title or '</article>' not in page:
            raise ValueError(f'{path.name}: missing article structure')
        if path.stem in RELATED_STORY_OVERRIDES:
            section = related_stories_section(RELATED_STORY_OVERRIDES[path.stem])
            if re.search(r'<section class="related-releases"[^>]*>.*?</section>', page, re.S):
                page = re.sub(r'<section class="related-releases"[^>]*>.*?</section>', section, page, count=1, flags=re.S)
            else:
                page = page.replace('</article>', section + '</article>', 1)
            page = re.sub(
                r'<script src="../assets/app\.js(?:\?v=[^"]*)?"></script>',
                '<script src="../assets/app.js?v=20261017-related-stories-v2"></script>',
                page,
                count=1,
            )
        else:
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
