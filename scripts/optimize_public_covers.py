#!/usr/bin/env python3
"""Build high-quality responsive WebP covers; retain original PNG URLs."""
from hashlib import sha256
import json
from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def encode_lossless(png):
    webp = png.with_suffix('.webp')
    with Image.open(png) as source:
        original = source.convert('RGBA')
        original.save(webp, format='WEBP', lossless=True, method=6, exact=True)
    with Image.open(webp) as encoded:
        decoded = encoded.convert('RGBA')
        if original.size != decoded.size or original.tobytes() != decoded.tobytes():
            webp.unlink()
            raise RuntimeError(f'Lossless pixel verification failed: {png.name}')
    if webp.stat().st_size >= png.stat().st_size:
        webp.unlink()
        return None
    return webp


def encode_responsive(png):
    """Keep full-resolution artwork plus smaller cards at WebP quality 90."""
    paths = []
    with Image.open(png) as source:
        original = source.convert('RGB')
        for width in (480, 800, 1200):
            target = png.with_name(png.stem + (f'-{width}' if width < 1200 else '') + '.webp')
            image = original if width == 1200 else original.resize((width, round(original.height * width / original.width)), Image.Resampling.LANCZOS)
            image.save(target, format='WEBP', quality=90, method=6)
            with Image.open(target) as decoded:
                if decoded.size != image.size:
                    raise RuntimeError(f'Invalid responsive cover: {target}')
            paths.append(target)
    return paths


def optimize_img(match, mapping):
    tag = match[0]
    source = re.search(r'\bsrc="([^"]+)"', tag)
    if not source or source[1] not in mapping:
        return tag
    url = mapping[source[1]]
    hero = 'article-original-cover' in tag
    candidates = f'{url} 1200w' if hero else f'{url[:-5]}-480.webp 480w, {url[:-5]}-800.webp 800w, {url} 1200w'
    sizes = '(max-width: 1200px) 100vw, 1200px' if hero else '(max-width: 600px) 92vw, (max-width: 1000px) 45vw, 400px'
    tag = re.sub(r'\s+(?:srcset|sizes)="[^"]*"', '', tag)
    return tag[:-1] + f' srcset="{candidates}" sizes="{sizes}">'


def replace_image_values(value, mapping):
    if isinstance(value, list):
        for item in value:
            replace_image_values(item, mapping)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {'image', 'cover'} and isinstance(item, str) and item in mapping:
                value[key] = mapping[item]
            else:
                replace_image_values(item, mapping)


def main():
    mapping = {}
    report = []
    for png in sorted((ROOT / 'assets/article-covers').glob('*.png')):
        variants = encode_responsive(png)
        webp = variants[-1]
        before = png.stat().st_size
        after = webp.stat().st_size if webp else before
        report.append({'file':png.name, 'pngBytes':before, 'displayBytes':after,
                       'quality':90, 'card480Bytes':variants[0].stat().st_size, 'card800Bytes':variants[1].stat().st_size})
        if webp:
            mapping['/' + png.relative_to(ROOT).as_posix()] = '/' + webp.relative_to(ROOT).as_posix()
    if not report:
        raise RuntimeError('No prepared PNG covers to optimize')
    # Preserve source, index metadata and social PNGs; change only rendered imgs.
    for page in [*ROOT.glob('*.html'), *(ROOT / 'articles').glob('*.html')]:
        source = page.read_text(encoding='utf-8')
        updated = re.sub(r'<img\b[^>]*>', lambda m:optimize_img(m, mapping), source, flags=re.I)
        if updated != source:
            page.write_text(updated, encoding='utf-8')
    # Runtime cards use catalog/feed image URLs, including search and schedules.
    for name in ['latest-news.json','popular-news.json','search-index.json','calendar-releases.json']:
        path = ROOT / 'assets' / name
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        replace_image_values(data, mapping)
        path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    catalog = ROOT / 'assets/data.js'
    source = catalog.read_text(encoding='utf-8')
    source = re.sub(r'((?:"image"|image|"cover"|cover)\s*:\s*")(/assets/article-covers/[a-z0-9-]+\.png)(")',
                    lambda m:m[1]+mapping.get(m[2],m[2])+m[3], source)
    catalog.write_text(source,encoding='utf-8')
    version = sha256(catalog.read_bytes()).hexdigest()[:16]
    for page in [*ROOT.glob('*.html'), *(ROOT / 'articles').glob('*.html')]:
        source = page.read_text(encoding='utf-8')
        source = re.sub(r'(src="(?:/|\.\./)?assets/data\.js)(?:\?[^"]*)?"',rf'\1?v={version}"',source)
        page.write_text(source,encoding='utf-8')
    out = ROOT / 'reports/responsive-covers.json'
    out.parent.mkdir(exist_ok=True)
    before = sum(x['pngBytes'] for x in report)
    after = sum(x['displayBytes'] for x in report)
    out.write_text(json.dumps({'covers':len(report),'optimized':len(mapping),
                             'pngBytes':before,'displayBytes':after,
                             'savedPercent':round(100*(1-after/before),2),
                             'files':report},indent=2)+'\n')
    print(f'Responsive covers: {len(mapping)}/{len(report)} optimized; '
          f'{before:,} → {after:,} bytes ({100*(1-after/before):.1f}% less); '
          'quality 90; 480/800/1200px variants validated. PNGs retained.')


if __name__ == '__main__':
    main()
