"""Make original title cards from the article headlines in the deployment."""
from base64 import b64decode
from hashlib import sha256
from html import unescape
from io import BytesIO
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps

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
    title = unescape(re.search(r"<title>(.*?)</title>", source, re.S)[1])
    title = re.sub(r"\s+(?:[|—–]|-)\s+AniNextUp\s*$", "", title).strip()
    illustration = artwork.get(page.stem)
    image = Image.new("RGB", (1200, 630), "#111930")
    if illustration:
        art = Image.open(BytesIO(b64decode(illustration["image"], validate=True))).convert("RGB")
        image = ImageOps.fit(art, (1200, 630), Image.Resampling.LANCZOS)
    if not illustration or not illustration.get("lettered"):
        draw_title(image, title, bool(illustration))
    image.save(OUT / (page.stem + ".png"), optimize=True)
    update_article(page, source)


def draw_title(image, title, illustrated):
    draw = ImageDraw.Draw(image, "RGBA")
    if illustrated:
        for x in range(850):
            shade = max(0, int(218 * (1 - (x / 850) ** 3)))
            draw.line((x, 0, x, 630), fill=(9, 12, 27, shade))
    else:
        draw.rectangle((68, 70, 1132, 560), outline="#604393", width=2)
        draw.rectangle((68, 70, 77, 560), fill="#a78bfa")
    draw.text((111, 115), "ANI NEXTUP", font=ImageFont.truetype(str(FONT), 24), fill="#c4b5fd")
    width = 700 if illustrated else 1010
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


def update_article(page, source):
    path = "/assets/article-covers/" + page.stem + ".png"
    source = re.sub(r'<meta\b(?=[^>]*(?:property|name)="(?:og:image(?::[^"]+)?|twitter:image(?::[^"]+)?)")[^>]*>', "", source, flags=re.I)
    metadata = (
        f'<meta property="og:image" content="{ORIGIN}{path}">'
        '<meta property="og:image:width" content="1200">'
        '<meta property="og:image:height" content="630">'
        f'<meta name="twitter:image" content="{ORIGIN}{path}">'
    )
    source = re.sub(r"</head>", metadata + "</head>", source, count=1, flags=re.I)
    cover = f'<img src="{path}" width="1200" height="630" alt="" decoding="async" class="article-original-cover">'
    source, count = re.subn(
        r'(<article\b[^>]*>\s*(?:<header\b[^>]*>.*?</header>\s*)?)',
        lambda m: m[0] + cover,
        source, count=1, flags=re.I | re.S,
    )
    if not count:
        raise ValueError(f"No article element: {page}")
    # Remove the old lead artwork placeholder if it follows the new card.
    source = re.sub(
        r'(<img[^>]+class="article-original-cover">)(\s*)(?:<figure\b[^>]*>\s*<img\b[^>]*anime-image-fallback\.svg[^>]*>.*?</figure>|<img\b[^>]*anime-image-fallback\.svg[^>]*>)',
        r'\1\2', source, count=1, flags=re.I | re.S,
    )
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
    for page in pages:
        build(page, artwork)
    # Static discovery cards and article recommendations share the same artwork.
    def replace_card(match):
        tag, body = match.groups()
        href = re.search(r'href="(?:https://aninextup\.com/)?(?:\.\./|/)?articles/([^"?#]+)', tag)
        if href and Path(href[1]).stem in artwork:
            cover = f"/assets/article-covers/{Path(href[1]).stem}.png"
            image_tag = re.compile(r"<img\b[^>]*>", re.I)
            def replace_image(image):
                img = re.sub(r'\s+(?:srcset|sizes|width|height|alt)="[^"]*"', "", image[0], flags=re.I)
                img = re.sub(r'\bsrc="[^"]*"', f'src="{cover}"', img, count=1, flags=re.I)
                return img[:-1] + ' width="1200" height="630" alt="" data-illustrated-cover>'
            body, count = image_tag.subn(replace_image, body, count=1)
            if not count and re.search(r'class="[^"]*\bvisual-card\b', tag):
                body = f'<img src="{cover}" width="1200" height="630" alt="" loading="lazy" data-illustrated-cover>' + body
        return tag + body + "</a>"

    for page in [*ROOT.glob("*.html"), *pages]:
        source = page.read_text(encoding="utf-8")
        updated = re.sub(r'(<a\b[^>]*>)(.*?)</a>', replace_card, source, flags=re.S)
        if updated != source:
            page.write_text(updated, encoding="utf-8")

    catalog = ROOT / "assets" / "data.js"
    def replace_catalog_image(match):
        entry = match[0]
        article = re.search(r'(?:"article"|article):"articles/([^"]+)"', entry)
        if not article or Path(article[1]).stem not in artwork:
            return entry
        cover = f"/assets/article-covers/{Path(article[1]).stem}.png"
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
                    if (OUT / (slug + ".png")).is_file():
                        for key in ("image", "cover"):
                            if key in value:
                                value[key] = f"/assets/article-covers/{slug}.png"
                for item in value.values():
                    refresh(item)
        refresh(data)
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    with (ROOT / "assets" / "style.css").open("a", encoding="utf-8") as css:
        css.write("\n.article-original-cover{display:block;width:100%;height:auto;border-radius:12px;margin:1.25rem 0}\nimg[data-illustrated-cover]{aspect-ratio:1200/630;object-fit:contain!important;height:auto}\n")
    print(f"Built {len(list(OUT.glob('*.png')))} original article covers")


if __name__ == "__main__":
    main()
