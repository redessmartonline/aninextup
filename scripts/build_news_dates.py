#!/usr/bin/env python3
"""Build News ordering from article dates, never from an anime's premiere date."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def article_dates(path):
    text = path.read_text(encoding="utf-8")
    published = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', text)
    if not published:
        return None
    # Visible editorial dates avoid promoting routine schema/asset maintenance.
    visible = re.search(r'<time\b[^>]*datetime=["\'](\d{4}-\d{2}-\d{2})', text)
    day = published.group(1)
    updated = max(day, visible.group(1)) if visible else day
    relative = path.relative_to(ROOT).as_posix()
    try:
        stamp = subprocess.check_output(
            ["git", "log", "-1", "--diff-filter=A", "--format=%ct", "--", relative],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        stamp = ""
    return {"published": day, "updated": updated, "publishedAt": int(stamp or 0)}


def main():
    dates = {}
    for path in sorted((ROOT / "articles").glob("*.html")):
        item = article_dates(path)
        if item:
            dates["articles/" + path.stem] = item
    payload = json.dumps(dates, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    output = "// Generated from article publication and visible update dates.\n"
    output += "var ANINEXTUP_NEWS_DATES=" + payload + ";\n"
    output += "if(typeof module!=='undefined')module.exports=ANINEXTUP_NEWS_DATES;\n"
    (ROOT / "assets/news-dates.js").write_text(output, encoding="utf-8")
    print(f"News dates: {len(dates)} articles")


if __name__ == "__main__":
    main()
