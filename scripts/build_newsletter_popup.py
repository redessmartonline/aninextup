"""Render the newsletter signup dialog in the shared public page build."""
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIALOG = '''
<dialog id="newsletter-popup" aria-labelledby="newsletter-popup-title" aria-describedby="newsletter-popup-intro">
  <button type="button" class="newsletter-popup-close" data-newsletter-dismiss aria-label="Close newsletter signup" autofocus>×</button>
  <span class="kicker">ANINEXTUP NEWSLETTER</span>
  <h2 id="newsletter-popup-title">Never miss an anime premiere</h2>
  <p id="newsletter-popup-intro">Get anime release dates, streaming updates and new guides in your inbox.</p>
  <form id="newsletter-popup-signup" action="/api/newsletter/subscribe" method="post" aria-describedby="newsletter-popup-status">
    <label for="newsletter-popup-email">Email address</label>
    <input id="newsletter-popup-email" name="email" type="email" maxlength="254" autocomplete="email" placeholder="Enter your email address" required disabled>
    <input type="hidden" name="consent" value="yes">
    <div hidden aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <button type="submit" disabled>Subscribe free</button>
  </form>
  <small>By subscribing, you agree to receive the AniNextUp newsletter. <a href="/privacy">Privacy Policy</a>. Unsubscribe anytime.</small>
  <p id="newsletter-popup-status" role="status">Checking subscription availability…</p>
</dialog>
'''


def asset(name):
    version = sha256((ROOT / 'assets' / name).read_bytes()).hexdigest()[:12]
    return f'/assets/{name}?v={version}'


def render(source):
    if '<header class="site-header">' not in source:
        return source
    source = re.sub(r'<dialog id="newsletter-popup".*?</dialog>\n?', '', source, flags=re.S)
    source = re.sub(r'<link\b[^>]*href="[^"]*assets/newsletter-popup\.css(?:\?[^"]*)?"[^>]*>\n?', '', source)
    source = re.sub(r'<script\b[^>]*src="[^"]*assets/newsletter\.js(?:\?[^"]*)?"[^>]*></script>\n?', '', source)
    css = f'<link rel="stylesheet" href="{asset("newsletter-popup.css")}">\n'
    source = source.replace('</head>', css + '</head>', 1)
    component = DIALOG.lstrip() + f'<script defer src="{asset("newsletter.js")}"></script>\n'
    source, count = re.subn(r'</body\s*>', lambda m: component + m[0], source, count=1, flags=re.I)
    return source if count else source + component


if __name__ == '__main__':
    pages = [*ROOT.glob('*.html'), *(ROOT / 'articles').glob('*.html')]
    for path in pages:
        original = path.read_text()
        updated = render(original)
        if updated != original:
            path.write_text(updated)
