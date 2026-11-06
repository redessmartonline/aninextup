"""Apply the external-tab policy to the public pages produced by the site build."""
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_HOSTS = {'aninextup.com', 'www.aninextup.com'}
VERSION = sha256((ROOT / 'assets/external-links.js').read_bytes()).hexdigest()[:12]
SCRIPT = f'<script defer src="/assets/external-links.js?v={VERSION}"></script>'
SCRIPT_TAG = re.compile(r'<script\b[^>]*\bsrc="(?:/|(?:\.\./)*)assets/external-links\.js(?:\?[^"]*)?"[^>]*>\s*</script>', re.I)


class ExternalLinks(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.edits = []

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attributes = dict(attrs)
        if 'download' in attributes:
            return
        try:
            url = urlsplit(attributes.get('href') or '')
        except ValueError:
            return
        if (url.scheme not in ('', 'http', 'https') or not url.hostname
                or url.hostname.rstrip('.') in INTERNAL_HOSTS):
            return
        rel = (attributes.get('rel') or '').lower().split()
        if attributes.get('target') == '_blank' and 'noopener' in rel and 'opener' not in rel:
            return
        attributes['target'] = '_blank'
        rel = [token for token in rel if token.lower() != 'opener']
        if 'noopener' not in rel:
            rel.append('noopener')
        attributes['rel'] = ' '.join(rel)
        opening = '<a' + ''.join(
            f' {name}="{escape(value, quote=True)}"' if value is not None else f' {name}'
            for name, value in attributes.items()
        ) + '>'
        line, column = self.getpos()
        start = self.offsets[line - 1] + column
        self.edits.append((start, start + len(self.get_starttag_text()), opening))

    def render(self):
        self.feed(self.source)
        self.close()
        source = self.source
        for start, end, replacement in reversed(self.edits):
            source = source[:start] + replacement + source[end:]
        source, count = SCRIPT_TAG.subn(lambda _: SCRIPT, source, count=1)
        if not count:
            source, count = re.subn(r'</body\s*>', lambda match: SCRIPT + match[0], source, count=1, flags=re.I)
            if not count:
                source += SCRIPT
        return source


if __name__ == '__main__':
    check = '--check' in sys.argv
    invalid = []
    pages = (path for folder in (ROOT, ROOT / 'articles', ROOT / 'previews', ROOT / 'editorial')
             for path in folder.glob('*.html'))
    for path in pages:
        source = path.read_text(encoding='utf-8')
        updated = ExternalLinks(source).render()
        if updated != source:
            if check:
                invalid.append(str(path.relative_to(ROOT)))
            else:
                path.write_text(updated, encoding='utf-8')
    if invalid:
        raise SystemExit('External-tab policy missing from: ' + ', '.join(invalid))
