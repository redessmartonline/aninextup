"""Make original title cards from the article headlines in the deployment."""
from html import unescape
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "article-covers"
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
ORIGIN = "https://aninextup.com"


def title_lines(title, font):
    lines = [""]
    for word in title.split():
        candidate = (lines[-1] + " " + word).strip()
        if lines[-1] and font.getlength(candidate) > 1010:
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def build(page):
    source = page.read_text(encoding="utf-8")
    title = unescape(re.search(r"<title>(.*?)</title>", source, re.S)[1])
    title = re.sub(r"\s+(?:[|—–]|-)\s+AniNextUp\s*$", "", title).strip()
    image = Image.new("RGB", (1200, 630), "#111930")
    draw = ImageDraw.Draw(image)
    draw.rectangle((68, 70, 1132, 560), outline="#604393", width=2)
    draw.rectangle((68, 70, 77, 560), fill="#a78bfa")
    draw.text((111, 115), "ANI NEXTUP", font=ImageFont.truetype(str(FONT), 24), fill="#c4b5fd")
    for size in range(68, 25, -2):
        font = ImageFont.truetype(str(FONT), size)
        lines = title_lines(title, font)
        if len(lines) <= 5 and all(font.getlength(line) <= 1010 for line in lines):
            break
    if len(lines) > 5 or any(font.getlength(line) > 1010 for line in lines):
        raise ValueError(f"Cover title does not fit: {page}")
    step = size + 10
    top = 337 - len(lines) * step // 2
    for number, line in enumerate(lines):
        draw.text((111, top + number * step), line, font=font, fill="#f5f2ff")
    image.save(OUT / (page.stem + ".png"), optimize=True)
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
    for page in pages:
        build(page)
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
        css.write("\n.article-original-cover{display:block;width:100%;height:auto;border-radius:12px;margin:1.25rem 0}\n")
    print(f"Built {len(list(OUT.glob('*.png')))} original article covers")


if __name__ == "__main__":
    main()
