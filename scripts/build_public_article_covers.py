"""Make original title cards from the article headlines in the deployment."""
from base64 import b64decode
from hashlib import sha256
from html import unescape
from io import BytesIO
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps

from draw_editorial_cover import draw_scene

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "article-covers"
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
ORIGIN = "https://aninextup.com"


def title_lines(title, font, width):
    lines = [""]
    for word in title.split():
        candidate = (lines[-1] + " " + word).strip()
        if lines[-1] and font.getlength(candidate) > width:
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def build(page, artwork):
    source = page.read_text(encoding="utf-8")
    # Keep established image URLs, including covers already shared externally.
    editorial = OUT / (page.stem + "-editorial.png")
    filename = editorial.name if editorial.is_file() else page.stem + ".png"

    title = unescape(re.search(r"<title>(.*?)</title>", source, re.S)[1])
    title = re.sub(r"\s+(?:[|—–]|-)\s+AniNextUp\s*$", "", title).strip()
    illustration = artwork.get(page.stem)
    image = Image.new("RGB", (1200, 630), "#111930")
    if illustration and "scene" in illustration:
        image = draw_scene(page.stem, illustration["scene"])
    elif illustration:
        if "file" in illustration:
            file = Path(__file__).with_name("cover-artwork") / illustration["file"]
            with Image.open(file) as original:
                if "panel" in illustration:
                    column, row = illustration["panel"]
                    width, height = original.size
                    # Trim the panel edges so an adjacent image cannot bleed into the cover.
                    left, right = width * column // 2, width * (column + 1) // 2
                    top, bottom = height * row // 4, height * (row + 1) // 4
                    inset = max(3, min(right - left, bottom - top) // 25)
                    art = original.crop((left + inset, top + inset, right - inset, bottom - inset)).convert("RGB")
                else:
                    art = original.convert("RGB")
        else:
            art = Image.open(BytesIO(b64decode(illustration["image"], validate=True))).convert("RGB")
        image = ImageOps.fit(art, (1200, 630), Image.Resampling.LANCZOS)
    if illustration and illustration.get("lettered"):
        raise ValueError(f"Cover needs an unlettered illustration: {page}")
    draw_title(image, title, page)
    image.save(OUT / filename, optimize=True)
    update_article(page, source, filename, 630)
    return filename, 630


def draw_title(image, title, page):
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(850):
        shade = int(218 * (1 - (x / 850) ** 3))
        draw.line((x, 0, x, 630), fill=(9, 12, 27, shade))
    draw.text((111, 115), "ANINEXTUP", font=ImageFont.truetype(str(FONT), 24), fill="#c4b5fd")
    width = 700
    for size in range(64, 25, -2):
        font = ImageFont.truetype(str(FONT), size)
        lines = title_lines(title, font, width)
        if len(lines) <= 5 and all(font.getlength(line) <= width for line in lines):
            break
    if len(lines) > 5 or any(font.getlength(line) > width for line in lines):
        raise ValueError(f"Cover title does not fit: {page}")
    step = size + 10
    top = 337 - len(lines) * step // 2
    for number, line in enumerate(lines):
        draw.text((111, top + number * step), line, font=font, fill="#f5f2ff")


def update_article(page, source, filename, height):
    path = "/assets/article-covers/" + filename
    source = re.sub(r'<meta\b(?=[^>]*(?:property|name)="(?:og:image(?::[^"]+)?|twitter:image(?::[^"]+)?)")[^>]*>', "", source, flags=re.I)
    metadata = (
        f'<meta property="og:image" content="{ORIGIN}{path}">'
        '<meta property="og:image:width" content="1200">'
        f'<meta property="og:image:height" content="{height}">'
        f'<meta name="twitter:image" content="{ORIGIN}{path}">'
    )
    source = re.sub(r"</head>", metadata + "</head>", source, count=1, flags=re.I)
    def update_image(match):
        data = json.loads(match[1])
        if 'id="aninextup-index"' in match[0].split(">", 1)[0]:
            data["image"] = path
        elif isinstance(data, dict) and data.get("@type") in {"Article", "NewsArticle", "BlogPosting"}:
            image = ORIGIN + path
            data["image"] = [image] if isinstance(data.get("image"), list) else image
        else:
            return match[0]
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
        return match[0].replace(match[1], payload, 1)

    source = re.sub(
        r'<script\b(?=[^>]*(?:type="application/ld\+json"|id="aninextup-index"))[^>]*>(.*?)</script>',
        update_image, source, flags=re.I | re.S,
    )

    cover = f'<img src="{path}" width="1200" height="{height}" alt="" decoding="async" class="article-original-cover">'
    article = re.search(r"<article\b[^>]*>(.*?)</article\s*>", source, flags=re.I | re.S)
    if not article:
        raise ValueError(f"No article element: {page}")
    body = article[1]
    heading = re.search(r"</h1\s*>", body, flags=re.I)
    if not heading:
        raise ValueError(f"No article heading: {page}")
    intro = re.match(
        r"""(?:\s*<p\b(?=[^>]*class=["'][^"']*\b(?:lead|byline)\b)[^>]*>.*?</p\s*>)*\s*(?:</(?:header|div)\s*>)?""",
        body[heading.end():],
        flags=re.I | re.S,
    )
    insert_at = article.start(1) + heading.end() + intro.end()
    source = source[:insert_at] + "\n" + cover + "\n" + source[insert_at:]
    # Replace the legacy lead image immediately after the new cover.
    legacy_hero = re.compile(
        r'(<img[^>]+class="article-original-cover">)\s*'
        r'(?:<figure\b[^>]*>\s*<img\b[^>]*>\s*(?:<figcaption\b[^>]*>(.*?)</figcaption\s*>)?\s*</figure\s*>'
        r'|<img\b[^>]*>)',
        flags=re.I | re.S,
    )

    source = legacy_hero.sub(r'\1\n', source, count=1)
    page.write_text(source, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    pages = sorted((ROOT / "articles").glob("*.html"))
    artwork = {}
    for manifest in sorted(Path(__file__).with_name("cover-artwork").glob("*.json")):
        batch = json.loads(manifest.read_text(encoding="utf-8"))
        if artwork.keys() & batch.keys():
            raise ValueError(f"Duplicate cover artwork in {manifest}")
        artwork.update(batch)
    covers = {page.stem: build(page, artwork) for page in pages}
    # Static discovery cards and article recommendations share the same artwork.
    def replace_card(match, page):
        tag, body = match.groups()
        href = re.search(r'href="(?:https://aninextup\.com/)?(?:\.\./|/)?articles/([^"?#]+)', tag)
        if not href and page.parent.name == "articles" and re.search(r'class="[^"]*\brelated-card\b', tag):
            href = re.search(r'href="(?:\./)?([a-z0-9-]+(?:\.html)?)(?=["?#])', tag)
        if href and Path(href[1]).stem in covers:
            filename, height = covers[Path(href[1]).stem]
            cover = f"/assets/article-covers/{filename}"
            image_tag = re.compile(r"<img\b[^>]*>", re.I)
            def replace_image(image):
                img = re.sub(r'\s+(?:srcset|sizes|width|height|alt)="[^"]*"', "", image[0], flags=re.I)
                img = re.sub(r'\bsrc="[^"]*"', f'src="{cover}"', img, count=1, flags=re.I)
                return img[:-1] + f' width="1200" height="{height}" alt="" data-illustrated-cover>'
            body, count = image_tag.subn(replace_image, body, count=1)
            if not count and re.search(r'class="[^"]*\b(?:visual-card|popular-news-card)\b', tag):
                body = f'<img src="{cover}" width="1200" height="{height}" alt="" loading="lazy" data-illustrated-cover>' + body
        return tag + body + "</a>"

    for page in [*ROOT.glob("*.html"), *pages]:
        source = page.read_text(encoding="utf-8")
        updated = re.sub(r'(<a\b[^>]*>)(.*?)</a>', lambda match: replace_card(match, page), source, flags=re.S)
        if updated != source:
            page.write_text(updated, encoding="utf-8")

    catalog = ROOT / "assets" / "data.js"
    def replace_catalog_image(match):
        entry = match[0]
        article = re.search(r'(?:"article"|article):"articles/([^"]+)"', entry)
        if not article or Path(article[1]).stem not in covers:
            return entry
        filename, _ = covers[Path(article[1]).stem]
        cover = f"/assets/article-covers/{filename}"
        return re.sub(r'((?:"image"|image):")[^"]+', lambda image: image[1] + cover, entry, count=1)
    catalog.write_text(re.sub(r'^\{[^\n]+', replace_catalog_image, catalog.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    # The published catalog differs from the pre-render input after artwork is assigned.
    version = sha256(catalog.read_bytes()).hexdigest()[:16]
    for page in [*ROOT.glob("*.html"), *pages]:
        source = page.read_text(encoding="utf-8")
        updated = re.sub(r'(src="(?:/|\.\./)?assets/data\.js)(?:\?[^"]*)?"', rf'\1?v={version}"', source)
        if updated != source:
            page.write_text(updated, encoding="utf-8")
    # Keep the dynamically rendered discovery cards aligned with their articles.
    for name in ("latest-news.json", "popular-news.json", "search-index.json", "calendar-releases.json"):
        path = ROOT / "assets" / name
        data = json.loads(path.read_text(encoding="utf-8"))
        def refresh(value):
            if isinstance(value, list):
                for item in value:
                    refresh(item)
            elif isinstance(value, dict):
                destination = value.get("article") or value.get("url") or value.get("href")
                if isinstance(destination, str) and destination.lstrip("/").startswith("articles/"):
                    slug = Path(destination).stem
                    if slug in covers:
                        filename, _ = covers[slug]
                        for key in ("image", "cover"):
                            if key in value:
                                value[key] = f"/assets/article-covers/{filename}"
                for item in value.values():
                    refresh(item)
        refresh(data)
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    with (ROOT / "assets" / "style.css").open("a", encoding="utf-8") as css:
        css.write("\n.article-original-cover{display:block;width:100%;height:auto;border-radius:12px;margin:1.25rem 0}\nimg[data-illustrated-cover]{aspect-ratio:1200/630;object-fit:contain!important;height:auto}\n")
        css.write("""
/* Keep a fixed image and text column in the homepage news archive. */
.home-page .popular-news-card > img {
  display: block;
  width: 100%;
  height: auto;
  min-height: 0;
  aspect-ratio: 1200 / 630;
  object-fit: contain;
}
#more-anime-news [data-home-more] > a.card.story.visual-card {
  --news-cover-width: 224px;
  gap: 16px !important;
  align-items: start;
  padding: 12px 0 !important;
  border-bottom: 1px solid var(--line);
}
#more-anime-news [data-home-more] > a.card.story.visual-card:not([hidden]) {
  display: grid !important;
  grid-template-columns: var(--news-cover-width) minmax(0, 1fr) !important;
}
#more-anime-news [data-home-more] > a.card.story.visual-card > img {
  grid-area: 1 / 1;
  display: block;
  width: var(--news-cover-width) !important;
  min-width: var(--news-cover-width);
  max-width: var(--news-cover-width);
  height: auto !important;
  aspect-ratio: 1200 / 630;
  margin: 0;
  border-radius: 6px;
  object-fit: contain;
}
#more-anime-news [data-home-more] > a.card.story.visual-card > .visual-body {
  grid-area: 1 / 2;
  min-width: 0;
  align-self: start;
  padding: 0;
}
#more-anime-news [data-home-more] .tag {
  font-size: .68rem;
  color: #c4aaff;
}
#more-anime-news [data-home-more] h3 {
  margin: 4px 0;
  font-size: 1rem;
  line-height: 1.28;
}
#more-anime-news [data-home-more] p {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  margin: 0;
  font-size: .88rem;
  line-height: 1.35;
  color: #b8c1d4;
}
#more-anime-news [data-home-more] .more {
  display: none;
}
@media (max-width: 700px) {
  .home-page .popular-news-card { flex-direction: column; }
}
@media (max-width: 580px) {
  #more-anime-news [data-home-more] > a.card.story.visual-card {
    --news-cover-width: clamp(122px, 35vw, 140px);
    gap: 10px !important;
  }
  #more-anime-news [data-home-more] h3 { font-size: .94rem; }
  #more-anime-news [data-home-more] p { font-size: .82rem; }
}
""")
    stylesheet = ROOT / "assets" / "style.css"
    style_version = sha256(stylesheet.read_bytes()).hexdigest()[:16]
    home = ROOT / "index.html"
    home_source = home.read_text(encoding="utf-8")
    home_source = re.sub(r'(href="(?:/)?assets/style\.css)(?:\?[^"]*)?"', rf'\1?v={style_version}"', home_source)
    home.write_text(home_source, encoding="utf-8")
    print(f"Built {len(list(OUT.glob('*.png')))} original article covers")


if __name__ == "__main__":
    main()
