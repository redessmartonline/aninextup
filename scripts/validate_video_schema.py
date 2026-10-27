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


class TrailerMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.index = None
        self.index_text = []
        self.players = []
        self.active_player = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and attrs.get('id') == 'aninextup-index':
            self.index = True
        if tag == 'div':
            if 'lite-trailer' in attrs.get('class', '').split():
                self.active_player = dict(attrs, button=False, image=False, overlay=False)
                self.players.append(self.active_player)
                self.depth = 1
            elif self.active_player is not None:
                self.depth += 1
        if self.active_player is not None:
            if tag == 'button' and 'trailer-play' in attrs.get('class', '').split():
                self.active_player['button'] = True
            if tag == 'img' and attrs.get('src'):
                self.active_player['image'] = True
            if 'trailer-overlay' in attrs.get('class', '').split():
                self.active_player['overlay'] = True

    def handle_data(self, value):
        if self.index:
            self.index_text.append(value)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.index = False
        if tag == 'div' and self.active_player is not None:
            self.depth -= 1
            if self.depth == 0:
                self.active_player = None


def trailer_markup_errors(text):
    """A recorded available official trailer must remain playable in the article."""
    parser = TrailerMarkup()
    parser.feed(text)
    if not parser.index_text:
        return []
    try:
        trailer = json.loads(''.join(parser.index_text)).get('trailer')
    except (ValueError, AttributeError):
        return ['Invalid article media metadata']
    if trailer is None:
        return []
    if not isinstance(trailer, dict) or not re.fullmatch(r'[A-Za-z0-9_-]{11}', str(trailer.get('youtubeId', ''))):
        return ['Invalid official trailer ID']
    if not all(trailer.get(key) for key in ('title', 'sourceUrl', 'thumbnail', 'verifiedOn')):
        return ['Official trailer is missing verification metadata']
    players = [player for player in parser.players if player.get('data-youtube') == trailer['youtubeId']]
    if len(parser.players) != 1 or len(players) != 1:
        return ['Available official trailer is missing or has a mismatched player']
    player = players[0]
    if player.get('data-external-only') == 'true' or not all(player[key] for key in ('button', 'image', 'overlay')):
        return ['Available official trailer requires an in-page play button, thumbnail and overlay']
    return []


def video_schema_errors(text):
    parser = StructuredData()
    parser.feed(text)
    errors = trailer_markup_errors(text)
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
