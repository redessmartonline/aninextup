#!/usr/bin/env python3
"""Remove legacy automatic inline recommendations; preserve editorial links.

Title-word overlap did not establish paragraph relevance. Only links marked by
the old generator are removed. Editors can add useful links directly, and the
separate Related releases cards remain intact.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = re.compile(r'\s*<span\s+data-aninextup-contextual=["\']1["\']>.*?</span>', re.S)

def main():
    changed = removed = 0
    for path in sorted((ROOT / "articles").glob("*.html")):
        original = path.read_text(encoding="utf-8")
        revised, count = GENERATED.subn('', original)
        if count:
            path.write_text(revised, encoding="utf-8")
            changed += 1
            removed += count
    print(f"Removed {removed} automatic inline recommendations from {changed} articles; editorial links and related cards preserved")

if __name__ == "__main__":
    main()

