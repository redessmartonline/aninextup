"""Use the AdSense tag to start Google's published consent message."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = re.compile(r"<script\b[^>]*>.*?</script>", re.I | re.S)
TAG = """<script data-aninextup-cmp>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{
  ad_storage:'denied', ad_user_data:'denied',
  ad_personalization:'denied', analytics_storage:'denied'
});
</script>
<script async crossorigin="anonymous" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6586052507600375"></script>"""


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
    return re.sub(r'(<head\b[^>]*>)', lambda m: m[0] + "\n" + TAG, source, count=1, flags=re.I)


def main():
    for page in [*ROOT.glob("*.html"), *(ROOT / "articles").glob("*.html")]:
        source = migrate(page.read_text(encoding="utf-8"))
        if source.count("data-aninextup-cmp") != 1 or "cookieconsent.run(" in source:
            raise ValueError(f"Invalid CMP migration: {page}")
        if page.name == "privacy.html":
            paragraphs = {
                "Our analytics initialization": "Analytics and Google Ads measurement tags are paused while we verify the site's consent integration.",
                "Our cookie interface is supplied": "Google's consent message manages advertising privacy choices for visitors in the European Economic Area, the United Kingdom and Switzerland. The site starts with optional Google consent settings declined.",
                "Select <strong>Update cookies preferences": "Where Google's consent message is available, use the privacy and cookie settings link that Google adds to the page to review or withdraw your choice.",
                "Our consent approach separates": "Google AdSense uses the choices made in Google's consent message to determine whether and how advertising may be served.",
                "Articles may include official trailers": "Articles may link to videos hosted on YouTube. When you follow a link, the destination's privacy and cookie policies apply.",
            }
            for opening, paragraph in paragraphs.items():
                source = re.sub(r"<p>" + re.escape(opening) + r".*?</p>", "<p>" + paragraph + "</p>", source, count=1, flags=re.S)
        page.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
