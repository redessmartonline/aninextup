#!/usr/bin/env python3
"""Prepare the deployable review build without third-party artwork or embedded video."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
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
    if re.fullmatch(r"https://aninextup\.com/assets/article-covers/[a-z0-9-]+\.(?:png|webp)", url):
        return url
    return (ORIGIN if url.startswith(("http://", "https://")) else "") + FALLBACK


def prepare(path):
    original = path.read_text(encoding="utf-8")
    content = original
    if path.suffix == ".html":
        # These credits described retired third-party illustrations, not the
        # original cover now generated for this article.
        content = re.sub(r'<p\b[^>]*class="[^"]*\bimage-credit\b[^"]*"[^>]*>.*?</p\s*>',
                         '', content, flags=re.I | re.S)
        def remove_image_download(match):
            from html import unescape
            href = unescape(match[1])
            if re.search(r'\.(?:avif|gif|jpe?g|png|svg|webp)(?:[/?#]|$)', href, re.I):
                return re.sub(r'<[^>]+>', '', match[2])
            return match[0]
        # Keep publisher articles and legal service links; retire direct image
        # file links for which the source archive has no reuse permission.
        content = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                         remove_image_download, content, flags=re.I | re.S)
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
        content = content.replace("is embedded below", "is linked below")
        content = content.replace("embedded preview", "video link")
        content = content.replace("The embedded clip", "The linked clip")
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



class PublicMedia(HTMLParser):
    """Inspect media loaded by the page. Editorial links are not embeds."""
    def __init__(self):
        super().__init__()
        self.urls = []
        self.embeds = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag in {"audio", "video", "iframe", "object", "embed"}:
            self.embeds.append(tag)
        if tag in {"img", "source", "image"}:
            self.urls.extend(fields[key] for key in
                             ("src", "data-src", "poster", "href", "xlink:href")
                             if fields.get(key))
            for key in ("srcset", "data-srcset"):
                self.urls.extend(item.strip().split()[0] for item in fields.get(key, "").split(",") if item.strip())
        if tag == "meta":
            name = fields.get("property", fields.get("name", "")).lower()
            if name in {"og:image", "og:image:url", "og:image:secure_url", "twitter:image", "twitter:image:src"} and fields.get("content"):
                self.urls.append(fields["content"])


def public_media_audit(files):
    pages = 0
    image_references = 0
    findings = []
    relative_image = re.compile(r'(?:/assets/(?:images/|article-covers/)[^"\'\s<>)]+)')
    css_images = re.compile(r'\burl\(\s*["\']?([^"\')]+)\s*["\']?\)', re.I)
    asset_dirs = {"article-covers"}
    allowed_assets = {"/assets/images/anime-image-fallback.svg", "/assets/favicon.svg"}
    for file in files:
        relative = file.relative_to(ROOT).as_posix()
        source = file.read_text(encoding="utf-8")
        refs = []
        embeds = []
        if file.suffix == ".html":
            pages += 1
            parser = PublicMedia()
            parser.feed(source)
            refs = parser.urls
            embeds = parser.embeds
            for href in re.findall(r'<a\b[^>]*href="([^"]+)"', source, re.I):
                if re.search(r'\.(?:avif|gif|jpe?g|png|svg|webp|torrent|mp4|mkv|zip|rar)(?:[/?#]|$)', href, re.I) or href.startswith('magnet:'):
                    findings.append(f"{relative}: unreviewed direct media/file link: {href[:220]}")
        if file.suffix in {".css", ".html"}:
            refs.extend(match.group(1).strip() for match in css_images.finditer(source)
                        if re.search(r'\.(?:svg|png|jpe?g|webp|gif|avif)(?:[?#]|$)', match.group(1).strip(), re.I))
        if file.suffix in {".js", ".json"}:
            refs.extend(relative_image.findall(source))
        for tag in set(embeds):
            findings.append(f"{relative}: embedded {tag}")
        for url in set(refs):
            image_references += 1
            resolved = urlsplit(urljoin(f"{ORIGIN}/{relative}", url))
            if resolved.netloc == "aninextup.com":
                parts = Path(resolved.path.lstrip("/")).parts
                if resolved.path in allowed_assets:
                    continue
                if (len(parts) == 3 and parts[0] == "assets" and parts[1] in asset_dirs
                        and re.fullmatch(r'[a-z0-9-]+\.(?:png|webp)', parts[2])
                        and (ROOT / resolved.path.lstrip("/")).is_file()):
                    continue
            findings.append(f"{relative}: image outside the published cover set: {url[:220]}")
    print(f"Copyright media inventory: {pages} HTML pages, {image_references} distinct image references per file, {len(findings)} findings.")
    for finding in findings:
        print(f"Copyright media review: {finding}")
    return findings


def main():
    files = [*ROOT.glob("*.html"), *(ROOT / "articles").glob("*.html")]
    files.extend(path for path in (ROOT / "assets").iterdir() if path.suffix in {".js", ".json", ".css"})
    for path in files:
        prepare(path)
    if public_media_audit(files):
        raise SystemExit('Deployment blocked: unresolved public media references')


if __name__ == "__main__":
    main()
