#!/usr/bin/env python3
"""Add relevant, verified internal article links without altering existing editorial text."""
import html
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
STOP = set("anime the and with from season release releases new announced announcement cast trailer teaser first second third date 2026 2027 2028 where watch premiere latest official update details film series manga tv more reveals streaming for has its will that this about".split())
SECTION = re.compile(r'(<div class="prose"[^>]*>)(.*?)(</div>)', re.S)
TITLE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)
PARA = re.compile(r'</p>', re.I)
MARKER = 'data-aninextup-contextual="1"'

def words(value):
    plain = html.unescape(re.sub(r'<[^>]+>', ' ', value)).lower()
    return set(w for w in re.findall(r'[a-z][a-z0-9-]{2,}', plain) if w not in STOP)

def main():
    paths = sorted(ARTICLES.glob("*.html"))
    docs = {p: p.read_text(encoding="utf-8") for p in paths}
    titles = {}
    for p, body in docs.items():
        match = TITLE.search(body)
        if match:
            titles[p] = html.unescape(re.sub(r'<[^>]+>', '', match.group(1))).strip()
    frequencies = Counter(w for title in titles.values() for w in words(title))
    changed = 0
    linked = 0
    for path, source in docs.items():
        match = SECTION.search(source)
        if not match:
            continue
        # Idempotence: remove only our own previously generated links.
        inner = re.sub(r'\s*<span data-aninextup-contextual="1">.*?</span>', '', match.group(2), flags=re.S)
        current_words = words(titles.get(path, ""))
        ranked = []
        for target, title in titles.items():
            if target == path:
                continue
            overlap = current_words & words(title)
            specific = {w for w in overlap if frequencies[w] <= 18}
            if not specific:
                continue
            score = sum(1 / max(1, frequencies[w]) for w in specific)
            ranked.append((score, target, title))
        ranked.sort(key=lambda item: (-item[0], item[1].name))
        paragraphs = list(PARA.finditer(inner))
        # The number is relevance-driven, never padded with unrelated links.
        budget = min(4, len(paragraphs) // 3, len(ranked))
        selected = [(target, title) for _, target, title in ranked[:budget]]
        if selected:
            offsets = []
            for i, (target, title) in enumerate(selected):
                position = paragraphs[min(len(paragraphs)-1, (i+1)*len(paragraphs)//(len(selected)+1))].start()
                href = html.escape(target.stem, quote=True)
                label = html.escape(title)
                snippet = f' <span {MARKER}>Related reading: <a href="{href}">{label}</a>.</span>'
                offsets.append((position, snippet))
            for position, snippet in reversed(offsets):
                inner = inner[:position] + snippet + inner[position:]
        revised = source[:match.start(2)] + inner + source[match.end(2):]
        # Every generated destination must be a real local article.
        for destination in re.findall(r'<span data-aninextup-contextual="1">.*?<a href="([^"]+)"', inner, re.S):
            if not (ARTICLES / (destination + ".html")).is_file() or destination == path.stem:
                raise ValueError(f"Invalid internal destination: {path.name} -> {destination}")
        if revised != source:
            path.write_text(revised, encoding="utf-8")
            changed += 1
        linked += len(selected)
    print(f"Updated {changed} articles; {linked} verified contextual links across {len(paths)} article files")

if __name__ == "__main__":
    main()
