#!/usr/bin/env python3
"""Install the Google Ads container inside TermsFeed's targeting category."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TAG_ID = "GTM-NL276DVG"
MARKER = '<script type="text/plain" data-cookie-consent="targeting" data-aninextup-ads>'
CONSENT = re.compile(
    r'<script\b[^>]*\bsrc="https://www\.termsfeed\.com/public/cookie-consent/[^"]+/cookie-consent\.js"[^>]*></script>'
)


def install(source, loader):
    block = f"{MARKER}\n{loader.rstrip()}\n</script>"
    if MARKER in source:
        if source.count(TAG_ID) != 1 or source.count(MARKER) != 1:
            raise ValueError("Duplicate Google Ads container")
        return re.sub(re.escape(MARKER) + r'.*?</script>', lambda _: block, source, count=1, flags=re.S)
    if TAG_ID in source:
        raise ValueError("Google Ads container is outside the managed consent block")
    if len(CONSENT.findall(source)) != 1:
        raise ValueError("Expected one TermsFeed consent loader")
    return CONSENT.sub(lambda match: match[0] + "\n" + block, source, count=1)


def main():
    loader = Path(__file__).with_name("google-ads-tag.js").read_text(encoding="utf-8")
    pages = [*ROOT.glob("*.html"), *(ROOT / "articles").glob("*.html")]
    for page in pages:
        source = page.read_text(encoding="utf-8")
        try:
            updated = install(source, loader)
        except ValueError as exc:
            raise SystemExit(f"{page.relative_to(ROOT)}: {exc}") from exc
        if source != updated:
            page.write_text(updated, encoding="utf-8")
    print(f"Installed consent-gated Google Ads on {len(pages)} pages")


if __name__ == "__main__":
    main()
