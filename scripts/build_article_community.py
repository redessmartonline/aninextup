"""Install the shared sharing/comment module on published article pages; idempotent."""
from pathlib import Path
from hashlib import sha256
from html import escape, unescape
from urllib.parse import quote, urlencode
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
BLOCK='''<section class="article-community" aria-label="Share and discuss this article"><div class="ac-share"><h2>Share this article</h2><p class="ac-sub">Know someone waiting for this anime? Send them the guide.</p><div class="ac-buttons"></div><p class="ac-share-status" role="status"></p></div><div class="ac-discussion"><div class="ac-heading"><h2>Join the discussion</h2><span class="ac-count">Comments</span></div><p class="ac-sub">Share your thoughts with other anime fans. Display names are chosen by readers.</p><form class="ac-form" method="post" action="/api/comments"><p class="ac-reply-note" hidden></p><label for="comment-name">Display name</label><input id="comment-name" name="name" minlength="2" maxlength="60" placeholder="How should we call you?" required autocomplete="off"><label for="comment-body">Your comment</label><textarea id="comment-body" name="body" minlength="3" maxlength="2000" placeholder="Add to the conversation. Please avoid spoilers." required></textarea><div class="ac-honey" hidden aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div><div class="ac-bottom"><p>Be respectful. No spam or personal information. Comments are reviewed before appearing. <a href="/privacy">Privacy Policy</a> · <a href="/contact">Report a comment</a></p><button class="ac-submit" type="submit" disabled>POST COMMENT →</button></div><p class="ac-status" role="status" aria-live="polite">Loading comments…</p></form><div class="ac-list"></div><button class="ac-load" type="button" hidden>Load more comments</button><noscript>Sharing and comments require JavaScript.</noscript></div></section>'''
def share_links(canonical, title):
    targets = (
        ('WhatsApp', 'https://wa.me/?' + urlencode({'text': f'{title} {canonical}'})),
        ('Facebook', 'https://www.facebook.com/sharer/sharer.php?' + urlencode({'u': canonical})),
        ('X', 'https://twitter.com/intent/tweet?' + urlencode({'url': canonical, 'text': title})),
        ('Reddit', 'https://www.reddit.com/submit?' + urlencode({'url': canonical, 'title': title})),
        ('Telegram', 'https://t.me/share/url?' + urlencode({'url': canonical, 'text': title})),
    )
    return ''.join(
        f'<a data-share-network="{name}" href="{escape(url)}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="Share on {name}"><span>{name}</span></a>'
        for name, url in targets
    )


def versioned_asset(ext):
    path = f'/assets/article-community.{ext}'
    version = sha256((ROOT / path.lstrip('/')).read_bytes()).hexdigest()[:12]
    return f'{path}?v={version}'


def render(path, text):
    if 'noindex' in text.split('</head>')[0]:
        return text
    if 'class="article-community"' not in text:
        match = re.search(r'<section\b[^>]*(?:aria-labelledby="related-releases-heading"|class="related-releases")[^>]*>', text)
        if not match:
            raise ValueError(f'Missing related section: {path}')
        text = text[:match.start()] + BLOCK + text[match.start():]

    title = re.search(r'<h1\b[^>]*>(.*?)</h1>', text, re.I | re.S)
    if not title:
        raise ValueError(f'Missing article heading: {path}')
    canonical = 'https://aninextup.com/articles/' + quote(path.stem)
    links = share_links(canonical, unescape(re.sub(r'<[^>]+>', '', title[1])).strip())
    text, count = re.subn(r'(<div class="ac-buttons">).*?(</div>)',
                          lambda m: m[1] + links + m[2], text, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one share container: {path}')
    for ext, attr, closing, tag in (
        ('css', 'href', '</head>', '<link rel="stylesheet" href="{}">'),
        ('js', 'src', '</body>', '<script defer src="{}"></script>'),
    ):
        url = versioned_asset(ext)
        pattern = rf'(?<={attr}=")(?:/|(?:\.\./)*)assets/article-community\.{ext}(?:\?[^"]*)?(?=")'
        text, count = re.subn(pattern, url, text)
        if not count:
            addition = tag.format(url)
            text = text.replace(closing, addition + closing, 1) if closing in text else text + addition
    return text


def main():
    check = '--check' in sys.argv
    changed = []
    for path in sorted((ROOT / 'articles').glob('*.html')):
        original = path.read_text()
        updated = render(path, original)
        if updated != original:
            changed.append(path.name)
            if not check:
                path.write_text(updated)
    if check and changed:
        raise SystemExit('Incomplete article community controls: ' + ', '.join(changed))
    print('Article community modules updated:', len(changed))
if __name__=='__main__':main()
