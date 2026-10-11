#!/usr/bin/env python3
"""Generate a reproducible editorial claims inventory; does not verify factual accuracy."""
import csv
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audits" / "editorial-claims-inventory.csv"
KEYWORDS = re.compile(r"premier|releas|stream|broadcast|air(?:s|ing)?\b|netflix|crunchyroll|prime video|disney\+|hulu|theater|cinema|schedule|season", re.I)
DATE = re.compile(r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)\s+\d{1,2}(?:,?\s+\d{4})?|20\d{2}|\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.|AM|PM|JST|ET|PT))\b", re.I)

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []
        self.links = []
        self.in_anchor = False
        self.anchor = []
        self.href = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"): self.skip += 1
        if tag == "a":
            self.in_anchor = True
            self.anchor = []
            self.href = a.get("href", "")
    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip = max(0, self.skip - 1)
        if tag == "a" and self.in_anchor:
            if self.href.startswith(("https://", "http://")):
                self.links.append((self.href, " ".join(self.anchor)))
            self.in_anchor = False
    def handle_data(self, data):
        if self.skip: return
        data = html.unescape(data).strip()
        if not data: return
        self.parts.append(data)
        if self.in_anchor: self.anchor.append(data)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for file in sorted((ROOT / "articles").rglob("*.html")):
        reader = Reader()
        reader.feed(file.read_text(encoding="utf-8", errors="replace"))
        text = re.sub(r"\s+", " ", " ".join(reader.parts))
        claims = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
        sources = [url for url, _ in reader.links if "aninextup.com" not in urllib.parse.urlsplit(url).netloc]
        for claim in claims:
            if not KEYWORDS.search(claim): continue
            if not (DATE.search(claim) or re.search(r"\b(?:confirmed|announced|available|exclusive|simulcast)\b", claim, re.I)): continue
            rows.append({"article":file.relative_to(ROOT).as_posix(),"claim":claim[:650],
                         "external_sources":" | ".join(dict.fromkeys(sources)),
                         "review_status":"NEEDS_MANUAL_SOURCE_COMPARISON",
                         "review_notes":""})
    with OUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["article","claim","external_sources","review_status","review_notes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Articles scanned: {len(list((ROOT / 'articles').rglob('*.html')))}")
    print(f"Candidate claims: {len(rows)}")
    print(f"Inventory: {OUT.relative_to(ROOT)}")
    print("All extracted claims are unverified; inspect official sources individually.")

if __name__ == "__main__": main()
