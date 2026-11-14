#!/usr/bin/env python3
"""Prepare the deployable review build without third-party artwork or embedded video."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FALLBACK = "/assets/images/anime-image-fallback.svg"
ORIGIN = "https://aninextup.com"
IMAGE_PATH = re.compile(
    r'(?:(?:https?://(?:www\.)?aninextup\.com)?/|(?:\.\./)*)(?:assets/images/)[^\s"\x27<>)?,]+(?:\?[^\s"\x27<>),]*)?',
    re.I,
)
REMOTE_IMAGE = re.compile(
    r'(?:https?:)?//[^\s"\x27<>,)]+?\.(?:avif|gif|jpe?g|png|svg|webp)(?:\?[^\s"\x27<>,)]*)?(?=["\x27\s<>,)]|$)',
    re.I,
)
PLAYER = re.compile(
    r'<div\b(?=[^>]*class="[^"]*\blite-trailer\b)[^>]*>\s*<button\b[^>]*>.*?</button>\s*</div>',
    re.I | re.S,
)
EMBED = re.compile(r'<(iframe|video|object)\b[^>]*>.*?</\1\s*>|<embed\b[^>]*>', re.I | re.S)
VIDEO_SCHEMA = re.compile(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.I | re.S)


def remove_video_schema(match):
    data = json.loads(match[1])
    if isinstance(data, dict) and data.get("@type") == "VideoObject":
        return ""
    if isinstance(data, dict) and isinstance(data.get("@graph"), list):
        graph = [item for item in data["@graph"] if item.get("@type") != "VideoObject"]
        if len(graph) != len(data["@graph"]):
            data["@graph"] = graph
            payload = json.dumps(data, ensure_ascii=False).replace("<", r"\u003c")
            payload = REMOTE_IMAGE.sub(use_fallback, IMAGE_PATH.sub(use_fallback, payload))
            return '<script type="application/ld+json">' + payload + '</script>'
    payload = REMOTE_IMAGE.sub(use_fallback, IMAGE_PATH.sub(use_fallback, match[1]))
    return match[0].replace(match[1], payload, 1)


def use_fallback(match):
    url = match[0]
    return (ORIGIN if url.startswith(("http://", "https://")) else "") + FALLBACK


def prepare(path):
    original = path.read_text(encoding="utf-8")
    content = original
    if path.suffix == ".html":
        def link_to_video(match):
            video_id = re.search(r'data-youtube="([A-Za-z0-9_-]{11})"', match[0])
            if not video_id:
                return ""
            url = "https://www.youtube.com/watch?v=" + video_id[1]
            return '<p><a href="' + url + '" target="_blank" rel="noopener noreferrer">Watch on YouTube</a></p>'
        content = PLAYER.sub(link_to_video, content)
        content = EMBED.sub("", content)
        content = re.sub(
            r'<script\b[^>]*>(?:(?!</script>).)*youtube-nocookie\.com/embed/(?:(?!</script>).)*</script>',
            "",
            content,
            flags=re.I | re.S,
        )
        content = content.replace("embedded player below", "video link below")
        content = content.replace("player below", "video link below")
        content = content.replace("The embedded player loads only when selected.", "The link opens the video on YouTube.")
        content = VIDEO_SCHEMA.sub(remove_video_schema, content)
        # Keep links to the cited publisher pages. Replace only image-loading
        # attributes and social previews so citations still lead to their source.
        def clean_tag(match):
            tag = match[0]
            if tag.lower().startswith("<img"):
                tag = re.sub(r'\s+srcset="[^"]*"', "", tag, flags=re.I)
                tag = re.sub(
                    r'(\s(?:src|data-src)=")(?:https?:)?//[^"]+',
                    lambda image: image[1] + FALLBACK,
                    tag,
                    flags=re.I,
                )
                if IMAGE_PATH.search(tag) or REMOTE_IMAGE.search(tag):
                    tag = re.sub(r'(\salt=)"[^"]*"', r'\1""', tag, flags=re.I)
            tag = REMOTE_IMAGE.sub(use_fallback, IMAGE_PATH.sub(use_fallback, tag))
            if tag.lower().startswith("<meta"):
                tag = tag.replace('content="' + FALLBACK, 'content="' + ORIGIN + FALLBACK)
            return tag
        content = re.sub(r'<(?:img|source|meta|link)\b[^>]*>', clean_tag, content, flags=re.I)
    else:
        content = IMAGE_PATH.sub(use_fallback, content)
        if path.suffix == ".json" or path.name == "data.js":
            content = REMOTE_IMAGE.sub(use_fallback, content)
    if path.name == "app.js":
        content, count = re.subn(
            r"^document\.querySelectorAll\('\.lite-trailer\[data-youtube\]'\)\.forEach.*$",
            "",
            content,
            flags=re.M,
        )
        if count == 0 and "youtube-nocookie.com/embed/" in content:
            raise RuntimeError("Embedded player could not be removed")
    if content != original:
        path.write_text(content, encoding="utf-8")


def main():
    files = [*ROOT.glob("*.html"), *(ROOT / "articles").glob("*.html")]
    files.extend(path for path in (ROOT / "assets").iterdir() if path.suffix in {".js", ".json", ".css"})
    for path in files:
        prepare(path)


if __name__ == "__main__":
    main()
