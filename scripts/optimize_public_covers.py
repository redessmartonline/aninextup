#!/usr/bin/env python3
"""Use pixel-identical lossless WebP covers; retain established PNG URLs."""
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


def optimize_img(match, mapping):
    tag = match[0]
    source = re.search(r'\bsrc="([^"]+)"', tag)
    if not source or source[1] not in mapping:
        return tag
    # A single full-resolution candidate preserves every pixel at every size.
    # Browsers without srcset support continue using the original PNG src.
    tag = re.sub(r'\s+srcset="[^"]*"', '', tag)
    return tag[:-1] + f' srcset="{mapping[source[1]]} 1x">'


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
        webp = encode_lossless(png)
        before = png.stat().st_size
        after = webp.stat().st_size if webp else before
        report.append({'file':png.name, 'pngBytes':before, 'displayBytes':after,
                       'pixelIdentical':True})
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
    out = ROOT / 'reports/lossless-covers.json'
    out.parent.mkdir(exist_ok=True)
    before = sum(x['pngBytes'] for x in report)
    after = sum(x['displayBytes'] for x in report)
    out.write_text(json.dumps({'covers':len(report),'optimized':len(mapping),
                             'pngBytes':before,'displayBytes':after,
                             'savedPercent':round(100*(1-after/before),2),
                             'files':report},indent=2)+'\n')
    print(f'Lossless covers: {len(mapping)}/{len(report)} optimized; '
          f'{before:,} → {after:,} bytes ({100*(1-after/before):.1f}% less); '
          'all decoded pixels verified identical. PNGs retained.')


if __name__ == '__main__':
    main()
