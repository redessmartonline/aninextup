"""Use the AdSense tag to start Google's published consent message."""
from hashlib import sha256
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = re.compile(r"<script\b[^>]*>.*?</script>", re.I | re.S)
TAG = """<script data-aninextup-cmp>
window['ga-disable-G-TRV5CF738D'] = true;
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{
  ad_storage:'denied', ad_user_data:'denied',
  ad_personalization:'denied', analytics_storage:'denied'
});
</script>
<script async crossorigin="anonymous" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6586052507600375"></script>"""


ANALYTICS_PANEL = """
<section id="analytics-consent" class="analytics-consent" data-analytics-consent hidden aria-labelledby="analytics-consent-title">
  <h2 id="analytics-consent-title">Analytics cookies</h2>
  <p>Allow Google Analytics to measure which pages people visit. You can change your choice anytime. <a href="/privacy">Privacy policy</a></p>
  <div class="analytics-consent-actions">
    <button type="button" data-analytics-choice="denied">Decline analytics</button>
    <button type="button" data-analytics-choice="granted">Allow analytics</button>
  </div>
</section>
<script defer src="/assets/analytics-consent.js?v=1"></script>
"""
SETTINGS = '<p><button type="button" class="analytics-settings" data-analytics-settings aria-controls="analytics-consent" aria-expanded="false">Analytics settings</button></p>'


def migrate(source):
    def remove_legacy(match):
        script = match[0]
        if any(marker in script for marker in (
            "termsfeed.com/public/cookie-consent", "cookieconsent.run(",
            "data-cookie-consent=", "data-aninextup-cmp", "adsbygoogle.js?client=",
        )):
            return ""
        return script

    source = SCRIPTS.sub(remove_legacy, source)
    source = re.sub(r'<noscript>[^<]*TermsFeed.*?</noscript>', '', source, flags=re.I | re.S)
    source = re.sub(r'<a\b[^>]*id="open_preferences_center"[^>]*>.*?</a>', '', source, flags=re.I | re.S)
    if 'data-analytics-settings' not in source:
        source = re.sub(r'</footer>', lambda m: SETTINGS + m[0], source, count=1, flags=re.I)
        source, inserted = re.subn(r'</body>', lambda m: ANALYTICS_PANEL + m[0], source, count=1, flags=re.I)
        if not inserted:
            source += ANALYTICS_PANEL
    return re.sub(r'(<head\b[^>]*>)', lambda m: m[0] + "\n" + TAG, source, count=1, flags=re.I)


def main():
    current_assets = {
        name: sha256((ROOT / "assets" / name).read_bytes()).hexdigest()[:16]
        for name in ("style.css", "app.js")
    }
    for page in [*ROOT.glob("*.html"), *(ROOT / "articles").glob("*.html")]:
        source = migrate(page.read_text(encoding="utf-8"))
        if source.count("data-aninextup-cmp") != 1 or "cookieconsent.run(" in source:
            raise ValueError(f"Invalid CMP migration: {page}")
        if source.count("data-analytics-settings") != 1 or source.count("data-analytics-consent") != 1:
            raise ValueError(f"Invalid CMP migration: {page}")
        if page.name == "privacy.html":
            paragraphs = {
                "Our analytics initialization": "Google Analytics measures page visits and interactions only after you choose Allow analytics. Use Analytics settings in the footer to review or withdraw your choice.",
                "Our cookie interface is supplied": "Google's consent message manages advertising privacy choices for visitors in the European Economic Area, the United Kingdom and Switzerland. Analytics consent is handled separately and starts declined.",
                "Select <strong>Update cookies preferences": "Use Analytics settings in the footer for analytics. Where Google's consent message is available, use its privacy and cookie settings link for advertising choices.",
                "Our consent approach separates": "Google AdSense uses the choices in Google's consent message for advertising. Your analytics choice does not grant advertising consent.",
                "Articles may include official trailers": "Articles may link to videos hosted on YouTube. When you follow a link, the destination's privacy and cookie policies apply.",
            }
            for opening, paragraph in paragraphs.items():
                source = re.sub(r"<p>" + re.escape(opening) + r".*?</p>", "<p>" + paragraph + "</p>", source, count=1, flags=re.S)
        for name, version in current_assets.items():
            pattern = rf'((?:href|src)="(?:/|\.\./)?assets/{re.escape(name)})(?:\?[^"]*)?"'
            source = re.sub(pattern, lambda m: f'{m[1]}?v={version}"', source)
        page.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
