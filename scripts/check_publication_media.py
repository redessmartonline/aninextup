#!/usr/bin/env python3
"""Block production publication of new or substantively revised articles without media review."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

from validate_publication import Audit, EditorialWords, validate
from validate_video_schema import TrailerMarkup

ROOT = Path(__file__).resolve().parents[1]
# Earlier articles retain their existing coverage until their editorial text changes.
BASELINE = 'efd44a6c99db8446d76d59bc1f6dc108d1ae5471'


def editorial_text(source):
    parser = EditorialWords()
    parser.feed(source)
    return re.findall(r"\b\w+(?:[’'-]\w+)*\b", ' '.join(parser.words))


def revised_articles():
    changed = subprocess.check_output(
        ['git', 'diff', '--name-only', '--diff-filter=AM', BASELINE, 'HEAD', '--', 'articles/'],
        cwd=ROOT, text=True
    ).splitlines()
    for name in changed:
        path = ROOT / name
        if path.suffix != '.html':
            continue
        previous = subprocess.run(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT,
                                  text=True, capture_output=True)
        source = path.read_text()
        if previous.returncode or editorial_text(previous.stdout) != editorial_text(source):
            yield path


def https_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == 'https' and bool(parsed.hostname)


def review_day(value):
    try:
        return date.fromisoformat(value).isoformat() == value
    except (TypeError, ValueError):
        return False


def reviewed_image(media, root):
    path = media.get('path')
    if not isinstance(path, str) or not path.startswith('/assets/images/'):
        return False
    file = (root / path.lstrip('/')).resolve()
    if not file.is_relative_to(root / 'assets/images') or not file.is_file():
        return False
    data = file.read_bytes()
    raster = (data.startswith((b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n'))
              or (data.startswith(b'RIFF') and data[8:12] == b'WEBP'))
    return (raster and hashlib.sha256(data).hexdigest() == media.get('sha256')
            and https_url(media.get('imageUrl')))


def media_errors(source, record, root=ROOT):
    errors = []
    audit = Audit()
    audit.feed(source)
    markup = TrailerMarkup()
    markup.feed(source)
    try:
        index = json.loads(''.join(markup.index_text))
    except ValueError:
        return errors + ['Missing or invalid article index metadata']

    cover = record.get('cover', {})
    review_fields = ('intent', 'keyword', 'verifiedOn')
    if not all(record.get(field) for field in review_fields) or not review_day(record.get('verifiedOn')):
        errors.append('Missing dated editorial review with search intent and keyword')
    hero = re.search(r'<figure\b[^>]*class="[^"]*\bofficial-hero\b[^"]*"[^>]*>.*?</figure>', source, re.S)
    figure = Audit()
    if hero:
        figure.feed(hero[0])
    social_images = {a.get('property') or a.get('name'): a.get('content')
                     for tag, a in audit.tags if tag == 'meta'}
    canonical_image = cover.get('path')
    if (not reviewed_image(cover, root) or not cover.get('credit') or
            not https_url(cover.get('sourceUrl')) or not figure.images or
            not figure.images[0].get('alt') or
            canonical_image != figure.images[0].get('src') or
            any(canonical_image != image for image in (
                social_images.get('og:image'), social_images.get('twitter:image'), index.get('image')
            )) or not any(link.get('href') == cover.get('sourceUrl') for link in figure.links)):
        errors.append('Official cover requires a reviewed raster file, credit, source and matching hero/social/index artwork')

    video = record.get('video', {})
    if video.get('status') == 'available':
        trailer = index.get('trailer', {})
        if (not trailer or video.get('youtubeId') != trailer.get('youtubeId') or
                not https_url(video.get('sourceUrl')) or video.get('sourceUrl') != trailer.get('sourceUrl') or
                not review_day(trailer.get('verifiedOn')) or not reviewed_image(video, root) or
                video.get('path') != trailer.get('thumbnail') or
                not any(player.get('imageSrc') == video.get('path') for player in markup.players) or
                not any(link.get('href') == 'https://www.youtube.com/watch?v=' + str(video.get('youtubeId'))
                        for link in audit.links)):
            errors.append('Available official teaser requires matching metadata, reviewed thumbnail and a YouTube fallback')
    elif video.get('status') == 'not-available':
        if not https_url(video.get('sourceUrl')) or not video.get('reason') or index.get('trailer') or markup.players:
            errors.append('Record the official source and reason when no relevant embeddable teaser is available')
    else:
        errors.append('Missing official trailer availability review')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', type=Path, nargs='*')
    args = parser.parse_args()
    paths = args.paths or list(revised_articles())
    failures = []
    for path in paths:
        record = ROOT / 'editorial/reviews' / (path.stem + '.json')
        if not record.is_file():
            failures.append(f'{path.name}: missing editorial review ({record.relative_to(ROOT)})')
            continue
        try:
            data = json.loads(record.read_text())
            errors = validate(path) + media_errors(path.read_text(), data)
        except (AttributeError, ValueError, TypeError) as exc:
            errors = [f'invalid review metadata: {exc}']
        failures.extend(f'{path.name}: {error}' for error in errors)
    for failure in failures:
        print(f'BLOCKED: {failure}')
    print(f'Publication media: {len(paths)} articles checked; {len(failures)} blocking findings')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
