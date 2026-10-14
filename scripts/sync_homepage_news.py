#!/usr/bin/env python3
"""Add newly published article pages to the AniNextUp homepage feed."""
import html
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "data.js"

def meta(source, key):
    pattern = r'<meta\s+[^>]*?(?:name|property)="' + re.escape(key) + r'"[^>]*?content="([^"]*)"'
    found = re.search(pattern, source, re.I)
    return html.unescape(found.group(1)) if found else ""

def article_entry(path):
    if not path.startswith("articles/") or not path.endswith(".html"):
        return None
    file = ROOT / path
    if not file.is_file():
        return None
    source = file.read_text(encoding="utf-8")
    if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', source, re.I):
        return None
    title = meta(source, "og:title")
    if not title:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.I | re.S)
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
    if not title:
        return None
    description = meta(source, "description")
    image = meta(source, "og:image") or meta(source, "twitter:image")
    if not image:
        m = re.search(r'<(?:figure[^>]*>\s*)?<img[^>]+src="([^"]+)"', source, re.I)
        image = html.unescape(m.group(1)) if m else ""
    if not image:
        return None  # Only show published stories with a real cover.
    url = path[:-5]
    return dict(id=pathlib.Path(url).name, image=image, title=title, tag="OFFICIAL NEWS",
                article=url, description=description)

def main():
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=AM", "HEAD^", "HEAD", "--", "articles/"],
        cwd=ROOT, text=True
    ).splitlines()
    if not changed:
        return
    data = DATA.read_text(encoding="utf-8")
    additions = []
    for path in changed:
        entry = article_entry(path)
        if entry and not re.search(r'article:"' + re.escape(entry["article"]) + r'"', data):
            additions.append(entry)
    if not additions:
        return
    lines = []
    for entry in additions:
        lines.append("{" + ",".join(k + ":" + json.dumps(v, ensure_ascii=False) for k, v in entry.items()) + "},")
    updated = data.replace("anime:[\n", "anime:\n" + "\n".join(lines) + "\n", 1)
    if updated == data:
        raise RuntimeError("Could not find anime array in assets/data.js")
    DATA.write_text(updated, encoding="utf-8")
    print("Added", len(additions), "new article(s) to homepage feed")

if __name__ == "__main__":
    main()
