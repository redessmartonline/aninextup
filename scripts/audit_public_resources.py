#!/usr/bin/env python3
"""Read-only external resource audit. HTTP results are not proof of video playback."""
import concurrent.futures
import datetime
import html.parser
import ipaddress
import re
import json
import pathlib
import socket
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "audits" / "runtime-external"
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (compatible; AniNextUpResourceAudit/1.0)"
class Extract(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.video_ids = []
    def handle_data(self, data):
        # VideoObject JSON-LD and JS data may contain embed URLs without iframe tags.
        for video in re.findall(r"(?:youtube(?:-nocookie)?\\.com/embed/|youtube\\.com/watch\\?v=|youtu\\.be/)([A-Za-z0-9_-]{11})", data):
            self.video_ids.append(video)
        for video in re.findall(r"i\\.ytimg\\.com/vi/([A-Za-z0-9_-]{11})/", data):
            self.video_ids.append(video)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in (("href",) if tag == "a" else ("src", "data-src") if tag in ("img", "iframe", "source") else ()):
            url = a.get(key, "").strip()
            if url.startswith("//"): url = "https:" + url
            if url.startswith(("https://", "http://")):
                kind = "image" if tag == "img" else "video" if ("youtube.com/embed/" in url or "youtube-nocookie.com/embed/" in url) else "link"
                self.refs.append((url, kind))
        for key in ("data-video-id", "data-youtube-id"):
            if a.get(key): self.video_ids.append(a[key])
        for key in ("src", "href", "data-src"):
            url = a.get(key, "")
            if "youtube.com/embed/" in url or "youtube-nocookie.com/embed/" in url:
                video = url.split("/embed/", 1)[1].split("?", 1)[0].split("/", 1)[0]
                if video: self.video_ids.append(video)
def safe_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("https", "http") or not p.hostname: return False
    if p.username or p.password or p.port not in (None, 80, 443): return False
    host = p.hostname.lower()
    if host in ("localhost",) or host.endswith((".local", ".internal")): return False
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return True
def request(url, method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"}, method=method)
    with urllib.request.urlopen(req, timeout=12) as res:
        final = res.geturl()
        if not safe_url(final): return {"status": "indeterminate", "reason": "unsafe_redirect"}
        if method == "GET": res.read(1024)
        return {"http_code": res.status, "final_url": final, "content_type": res.headers.get("Content-Type", "")}
def check(item):
    url, kind, pages = item
    record = {"url": url, "kind": kind, "articles": sorted(pages)}
    if not safe_url(url):
        record.update(status="indeterminate", reason="non_public_or_unsupported_url")
        return record
    try:
        data = request(url, "GET")
        record.update(data)
        if "status" not in record:
            ct = data.get("content_type", "").lower()
            if kind == "image" and not ct.startswith("image/"):
                record.update(status="indeterminate", reason="not_image_content_type")
            else: record["status"] = "accessible"
    except urllib.error.HTTPError as e:
        record.update(http_code=e.code, status="broken" if e.code in (404, 410) else "indeterminate", reason="http_error")
    except Exception as e:
        record.update(status="indeterminate", reason=type(e).__name__)
    return record
def main():
    refs = {}
    videos = {}
    pages = list((ROOT / "articles").rglob("*.html"))
    for path in pages:
        parser = Extract()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        rel = str(path.relative_to(ROOT))
        for url, kind in parser.refs:
            key = (url, kind)
            refs.setdefault(key, set()).add(rel)
        for video in parser.video_ids:
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", video):
                videos.setdefault(video, set()).add(rel)
    jobs = [(u, k, p) for (u, k), p in refs.items()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(check, jobs))
    video_results = []
    for vid, linked in sorted(videos.items()):
        # oEmbed can check public metadata but cannot prove embed playback.
        url = "https://www.youtube.com/oembed?url=" + urllib.parse.quote("https://www.youtube.com/watch?v=" + vid, safe="") + "&format=json"
        r = check((url, "video_metadata", linked))
        r["video_id"] = vid
        r["playback_verified"] = False
        video_results.append(r)
    result = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "scope": "read_only_external_http_and_youtube_oembed",
      "articles_scanned": len(pages),
      "limitations": ["HTTP 403/429 and timeouts are indeterminate, not broken.",
       "YouTube oEmbed availability does not prove playback or embed permission.",
       "HTTP 200 for an image does not guarantee correct licensing or editorial use.",
       "Image and link inventory covers HTML attributes; video IDs also include embedded JSON-LD and script text.",
       "YouTube metadata requests may be blocked even when a video is public."],
      "resources": results, "videos": video_results,
      "summary": {"external_references": len(results), "image_references": sum(r["kind"]=="image" for r in results),
        "youtube_ids": len(video_results),
        "accessible": sum(r["status"]=="accessible" for r in results),
        "broken": sum(r["status"]=="broken" for r in results),
        "indeterminate": sum(r["status"]=="indeterminate" for r in results)}}
    (OUT / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    lines = ["# AniNextUp public resource audit", "", f"Articles scanned: {len(pages)}", f"External references: {len(results)}", f"Images: {result['summary']['image_references']}", f"YouTube IDs: {len(video_results)}", "", "## HTTP summary", ""]
    lines.extend(f"- {key}: {result['summary'][key]}" for key in ("accessible","broken","indeterminate"))
    lines += ["", "## Broken (HTTP 404/410)", ""]
    lines.extend(f"- {r['http_code']} {r['url']} ({', '.join(r['articles'])})" for r in results if r["status"]=="broken")
    lines += ["", "## Limitations", ""]
    lines.extend("- " + s for s in result["limitations"])
    (OUT / "summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))
    print("Video playback remains unverified; see artifact for per-URL results.")
if __name__ == "__main__": main()
