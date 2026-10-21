#!/usr/bin/env python3
"""Validate video upload dates without inferring them from article dates."""
import argparse
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import re


class StructuredData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type', '').lower() == 'application/ld+json':
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.current is not None:
            self.blocks.append(''.join(self.current))
            self.current = None


def video_objects(value):
    if isinstance(value, dict):
        types = value.get('@type', [])
        if types == 'VideoObject' or isinstance(types, list) and 'VideoObject' in types:
            yield value
        for child in value.values():
            yield from video_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from video_objects(child)


def valid_upload_date(value):
    if not isinstance(value, str):
        return False
    try:
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            return False
    except ValueError:
        return False
    return True


def video_schema_errors(text):
    parser = StructuredData()
    parser.feed(text)
    errors = []
    for block in parser.blocks:
        try:
            data = json.loads(block)
        except ValueError:
            errors.append('Invalid JSON-LD')
            continue
        for video in video_objects(data):
            if not valid_upload_date(video.get('uploadDate')):
                errors.append('VideoObject missing or invalid uploadDate (require a verified publication timestamp with timezone)')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', type=Path)
    args = parser.parse_args()
    paths = args.paths or sorted(Path('articles').glob('*.html'))
    if not paths:
        parser.error('No article HTML files found')
    failures = []
    for path in paths:
        failures.extend(f'{path}: {error}' for error in video_schema_errors(path.read_text(encoding='utf-8')))
    for failure in failures:
        print(failure)
    print(f'Video schema: {len(paths)} articles checked; {len(failures)} errors')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
