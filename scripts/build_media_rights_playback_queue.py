#!/usr/bin/env python3
"""Generate a reproducible media-rights and playback review queue for every article.

Inventory only: never infer a license or actual video playback from an HTTP response.
"""
import csv
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audits" / "generated"

class Media(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.videos = set()
        self.text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            src = a.get("src") or a.get("data-src") or ""
            if src: self.images.append((src, a.get("alt", "")))
        for key in ("data-video-id", "data-youtube-id"):
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", a.get(key, "")):
                self.videos.add(a[key])
        for key in ("src", "href"):
            self.videos.update(re.findall(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/)([A-Za-z0-9_-]{11})", a.get(key, "")))
    def handle_data(self, data):
        self.videos.update(re.findall(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/|i\.ytimg\.com/vi/)([A-Za-z0-9_-]{11})", data))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    image_rows, video_rows, article_rows = [], [], []
    pages = sorted((ROOT / "articles").glob("*.html"))
    for path in pages:
        parser = Media()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        name = path.relative_to(ROOT).as_posix()
        for src, alt in sorted(set(parser.images)):
            host = urlsplit(src).hostname or ""
            external = bool(host and host not in ("aninextup.com", "www.aninextup.com"))
            image_rows.append({"article":name, "image_url":src, "alt":alt, "externally_hosted":external,
                               "reuse_permission":"UNVERIFIED", "license_evidence_url":"", "review_notes":""})
        for video in sorted(parser.videos):
            video_rows.append({"article":name, "youtube_id":video, "official_video_provenance":"UNVERIFIED",
                               "real_browser_playback":"NOT_TESTED", "region_tested":"", "test_notes":""})
        article_rows.append({"article":name, "image_references":len(parser.images), "youtube_ids":len(parser.videos),
                             "all_factual_claims_checked":"NO", "all_image_rights_cleared":"NO",
                             "all_videos_playback_tested":"NO"})
    def write(name, fields, rows):
        with (OUT / name).open("w", encoding="utf-8", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    write("media-image-rights-queue.csv",
          ["article","image_url","alt","externally_hosted","reuse_permission","license_evidence_url","review_notes"], image_rows)
    write("media-video-playback-queue.csv",
          ["article","youtube_id","official_video_provenance","real_browser_playback","region_tested","test_notes"], video_rows)
    write("editorial-manual-completion-queue.csv",
          ["article","image_references","youtube_ids","all_factual_claims_checked","all_image_rights_cleared","all_videos_playback_tested"], article_rows)
    print(f"Articles: {len(article_rows)}; image references: {len(image_rows)}; video/article references: {len(video_rows)}")
    print("All rights, factual completeness and browser playback fields remain unverified until independently checked.")

if __name__ == "__main__":
    main()
