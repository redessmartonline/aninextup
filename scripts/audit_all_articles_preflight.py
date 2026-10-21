#!/usr/bin/env python3
"""Read-only, reproducible preflight of every published AniNextUp article."""
import argparse
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from validate_video_schema import video_schema_errors
from editorial_dates import editorial_date_errors

def attr(tag, key):
    m = re.search(r'\b' + re.escape(key) + r'\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
    return html.unescape(m.group(2)) if m else None

def meta(text, key, value):
    for tag in re.findall(r'<meta\b[^>]*>', text, re.I | re.S):
        if attr(tag, key) == value:
            return attr(tag, 'content')
    return None

def audit(path):
    text = path.read_text(encoding='utf-8')
    issues = [("error", "invalid_video_upload_date") for error in video_schema_errors(text)]
    if 'googletagmanager.com/gtag/js?id=G-TRV5CF738D' not in text:
        issues.append(('error', 'missing_ga4_tag'))
    issues.extend(('error', error) for error in editorial_date_errors(text))
    title = re.search(r'<title\b[^>]*>(.*?)</title>', text, re.I | re.S)
    if not title or not re.sub(r'<[^>]*>', '', title.group(1)).strip():
        issues.append(('error', 'missing_title'))
    if not meta(text, 'name', 'description'):
        issues.append(('warning', 'missing_description'))
    canonical = None
    for tag in re.findall(r'<link\b[^>]*>', text, re.I | re.S):
        if attr(tag, 'rel') == 'canonical':
            canonical = attr(tag, 'href')
            break
    if not canonical:
        issues.append(('warning', 'missing_canonical'))
    elif urlparse(canonical).netloc.lower() not in ('aninextup.com', 'www.aninextup.com'):
        issues.append(('error', 'external_canonical'))
    elif urlparse(canonical).path.rstrip('/').removesuffix('.html') != '/articles/' + path.stem:
        issues.append(('warning', 'canonical_slug_mismatch'))
    if not meta(text, 'property', 'og:image'):
        issues.append(('warning', 'missing_og_image'))
    for tag in re.findall(r'<img\b[^>]*>', text, re.I | re.S):
        if attr(tag, 'alt') is None:
            issues.append(('warning', 'image_missing_alt'))
    index_blocks = re.findall(r'<script\b(?=[^>]*\bid=["\']aninextup-index["\'])[^>]*>(.*?)</script>', text, re.I | re.S)
    for block in index_blocks:
        try:
            data = json.loads(block)
            if not isinstance(data, dict) or not data.get('title') or not data.get('image'):
                issues.append(('error', 'incomplete_article_index'))
        except json.JSONDecodeError:
            issues.append(('error', 'invalid_article_index_json'))
    ld_count = 0
    for tag, body in re.findall(r'(<script\b[^>]*>)(.*?)</script>', text, re.I | re.S):
        if attr(tag, 'type') == 'application/ld+json':
            ld_count += 1
            try:
                json.loads(body)
            except json.JSONDecodeError:
                issues.append(('error', 'invalid_json_ld'))
    if not ld_count:
        issues.append(('warning', 'missing_json_ld'))
    youtube_ids = sorted(set(re.findall(r'(?:youtube\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{11})', text)))
    images = [attr(t, 'src') for t in re.findall(r'<img\b[^>]*>', text, re.I | re.S)]
    external_images = sorted(set(u for u in images if u and urlparse(u).scheme in ('http', 'https') and urlparse(u).netloc not in ('aninextup.com', 'www.aninextup.com')))
    return {'file': str(path).replace('\\', '/'), 'issues': [{'severity': s, 'code': c} for s, c in sorted(set(issues))], 'youtube_ids': youtube_ids, 'external_images': external_images, 'json_ld_blocks': ld_count, 'article_index_present': bool(index_blocks)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='articles')
    parser.add_argument('--out', default='audits/generated')
    args = parser.parse_args()
    paths = sorted(Path(args.root).glob('*.html'))
    if not paths:
        raise SystemExit('ERROR: no article HTML files found')
    rows = [audit(p) for p in paths]
    counts = Counter(i['code'] for row in rows for i in row['issues'])
    result = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'total_articles': len(rows), 'total_error_findings': sum(i['severity']=='error' for row in rows for i in row['issues']), 'total_warning_findings': sum(i['severity']=='warning' for row in rows for i in row['issues']), 'issue_counts': dict(sorted(counts.items())), 'articles': rows, 'limitations': ['Static HTML inspection only: no HTTP/browser playback tests', 'No copyright or image reuse permission verification', 'No factual claim verification', 'Legacy pages are not required to have an aninextup-index block']}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out/'all-articles-preflight.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    lines = ['# All published articles — reproducible preflight', '', f"Total articles: **{len(rows)}**", f"Errors: **{result['total_error_findings']}**; warnings: **{result['total_warning_findings']}**", '', '## Issue counts', '']
    lines += [f'- {k}: {v}' for k, v in sorted(counts.items())] or ['- None']
    lines += ['', '## Article findings', '', '| Article | Errors / warnings | YouTube IDs | External image URLs |', '|---|---|---:|---:|']
    for row in rows:
        codes = ', '.join(i['code'] for i in row['issues']) or 'None'
        lines.append(f"| {Path(row['file']).name} | {codes} | {len(row['youtube_ids'])} | {len(row['external_images'])} |")
    lines += ['', '## Important limitations', '', '- This is a static audit; it does not prove that trailers play or that images load publicly.', '- External image presence is not a license or copyright clearance.', '- It does not validate the truth of article claims.', '- Legacy articles without aninextup-index are not flagged merely for lacking the optional block.', '- Findings must be checked before published content is edited.', '']
    (out/'all-articles-preflight.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f"Audited {len(rows)} articles; errors={result['total_error_findings']}; warnings={result['total_warning_findings']}")
    for k, v in sorted(counts.items()):
        print(f'{k}: {v}')
    if result['total_error_findings']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
