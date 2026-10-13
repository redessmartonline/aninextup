#!/usr/bin/env python3
"""Block new AniNextUp article files that duplicate an existing subject."""
from pathlib import Path
from html.parser import HTMLParser
import re
import subprocess
import sys
import unicodedata

STOP = {"anime", "season", "release", "date", "trailer", "cast", "staff", "news", "official", "new", "update", "announced", "confirmed", "2026", "2027", "movie", "tv", "and", "the", "for", "with", "adds", "five", "members", "ahead", "of", "premiere"}

def normalized(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", s)

def topic_tokens(s):
    return set(normalized(s)) - STOP

def article_title(path):
    s = path.read_text(encoding="utf-8")
    m = re.search(r"<h1\\b[^>]*>(.*?)</h1>", s, re.I | re.S)
    if not m:
        raise ValueError(f"No H1 in {path}")
    return re.sub(r"<[^>]+>", " ", m.group(1)).strip()

def check(new_path, existing_paths):
    candidate = topic_tokens(article_title(new_path))
    if not candidate:
        return [f"Cannot identify subject of {new_path}"]
    problems = []
    for path in existing_paths:
        if path == new_path:
            continue
        title = article_title(path)
        other = topic_tokens(title)
        if not other:
            continue
        # All significant subject tokens of one title are contained in the other:
        # fail closed, then have an editor decide whether to UPDATE the original.
        smaller, larger = (candidate, other) if len(candidate) <= len(other) else (other, candidate)
        if len(smaller) >= 1 and smaller.issubset(larger):
            problems.append(f"Possible duplicate: {new_path} vs {path} ({title}). UPDATE existing canonical instead.")
    return problems

def main():
    base = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD", "articles/"], text=True).splitlines())
    new = [Path(p) for p in subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "articles/"], text=True).splitlines() if p.endswith(".html")]
    # Also handle files staged or modified in a branch relative to the current base.
    existing = [Path(p) for p in base if p.endswith(".html") and Path(p).is_file()]
    errors = []
    for path in new:
        errors += check(path, existing)
    if errors:
        for error in errors:
            print("BLOCKED: " + error, file=sys.stderr)
        return 1
    print(f"PASS: checked {len(new)} new article(s) against {len(existing)} existing article(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
