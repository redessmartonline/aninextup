#!/usr/bin/env python3
"""AniNextUp public resource and editorial similarity audit (standard library)."""
import concurrent.futures
import datetime
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://aninextup.com"
UA = "AniNextUpQualityAudit/1.0 (+https://aninextup.com/contact)"
TIMEOUT = 15

def request(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read(200000)
            return {"status": resp.status, "final_url": resp.url, "content_type": resp.headers.get("Content-Type", ""), "bytes_sampled": len(data)}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "error": str(exc), "final_url": exc.url}
    except Exception as exc:
        return {"status": None, "error": str(exc)[:240]}

def main():
    sitemap = ET.parse(ROOT / "sitemap.xml")
    urls = [x.text.strip() for x in sitemap.findall(".//{*}loc") if x.text]
    article_paths = sorted((ROOT / "articles").glob("*.html"))
    refs = defaultdict(set)
    articles = {}
    for p in article_paths:
        s = p.read_text(encoding="utf-8")
        article_url = BASE + "/articles/" + p.stem
        body = re.search(r'<div class="prose"[^>]*>(.*?)</div>', s, re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", body.group(1) if body else s))
        text = re.sub(r"\s+", " ", text).strip()
        articles[p.stem] = {"word_count": len(text.split()), "text": text}
        for value in re.findall(r'(?:href|src|poster|data-src)="([^"]+)"', s):
            value = html.unescape(value).strip()
            if value.startswith(("http://", "https://")):
                refs[value].add(article_url)
            elif value.startswith(("../", "/")) and not value.startswith("//"):
                resolved = urllib.parse.urljoin(article_url, value)
                if resolved.startswith(BASE):
                    refs[resolved].add(article_url)
        for vid in re.findall(r'data-youtube="([A-Za-z0-9_-]{11})"', s):
            refs["https://www.youtube.com/watch?v=" + vid].add(article_url)
    # Verify public sitemap URLs as well as referenced external media and links.
    for url in urls:
        refs[url].add("sitemap.xml")
    refs[BASE + "/assets/app.js"].add("site-assets")
    refs[BASE + "/assets/data.js"].add("site-assets")
    checked = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        future_map = {pool.submit(request, u): u for u in refs}
        for future in concurrent.futures.as_completed(future_map):
            checked[future_map[future]] = future.result()
    # Near-duplicate screening: word-shingle Jaccard, not a plagiarism verdict.
    shingles = {}
    for name, entry in articles.items():
        tokens = re.findall(r"[a-z0-9]+", entry["text"].lower())
        shingles[name] = set(zip(*(tokens[i:] for i in range(5)))) if len(tokens) >= 5 else set()
    near_duplicates = []
    names = sorted(shingles)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, sb = shingles[a], shingles[b]
            if not sa or not sb:
                continue
            similarity = len(sa & sb) / len(sa | sb)
            if similarity >= .35:
                near_duplicates.append({"a": a, "b": b, "shingle_jaccard": round(similarity, 3)})
    results = []
    for url, data in sorted(checked.items()):
        code = data.get("status")
        results.append({"url": url, "sources": sorted(refs[url]), **data,
                        "assessment": "ok" if code and 200 <= code < 400 else
                        "needs_manual_check" if code in (401, 403, 429) else "failed_or_unverified"})
    report = {"checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "sitemap_url_count": len(urls), "article_file_count": len(article_paths),
              "unique_urls_checked": len(results),
              "ok": sum(x["assessment"] == "ok" for x in results),
              "needs_manual_check": sum(x["assessment"] == "needs_manual_check" for x in results),
              "failed_or_unverified": sum(x["assessment"] == "failed_or_unverified" for x in results),
              "url_results": results,
              "near_duplicate_candidates": near_duplicates,
              "short_articles_under_150_words": [{"article": n, "words": e["word_count"]} for n,e in articles.items() if e["word_count"] < 150],
              "editorial_fact_check": "Manual official-source comparison still required; HTTP success is not factual verification."}
    path = ROOT / "audit-results.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Checked {len(results)} URLs: {report['ok']} OK, {report['needs_manual_check']} blocked/rate-limited, {report['failed_or_unverified']} failed/unverified")
    print(f"Near-duplicate candidates: {len(near_duplicates)}. Report: {path}")
    for item in results:
        if item["assessment"] != "ok":
            print(f"CHECK {item['assessment']} HTTP={item.get('status')} URL={item['url']} ERROR={item.get('error', '')}")
    for item in report["short_articles_under_150_words"]:
        print(f"SHORT ARTICLE {item['words']} words: {item['article']}")
    # Fail only on verified broken URLs, not blocked or DNS/timeouts.
    hard_fail = [x for x in results if x.get("status") in (404, 410) and x["url"].startswith(BASE)]
    if hard_fail:
        print(f"ERROR: {len(hard_fail)} first-party URLs returned 404/410", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
