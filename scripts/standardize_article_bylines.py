#!/usr/bin/env python3
"""Unify visible bylines using original editorial publication dates only."""
from pathlib import Path
from html.parser import HTMLParser
from datetime import date
import json
import re
from editorial_dates import article_metadata, iso_day

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer(r'\n', text))
        self.nodes = []
        self.stack = []
        self.feed(text)
    def position_offset(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col
    def handle_starttag(self, tag, attrs):
        start = self.position_offset()
        node = {'tag':tag,'attrs':dict(attrs),'start':start,'open_end':start+len(self.get_starttag_text()),'parent':self.stack[-1] if self.stack else None}
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                node = self.stack[i]
                node['close_start'] = self.position_offset()
                node['end'] = self.text.find('>', self.position_offset()) + 1
                self.stack = self.stack[:i]
                break

def has_class(node, name):
    return name in node['attrs'].get('class','').split()

def normalize(text):
    parsed = Elements(text)
    articles = [n for n in parsed.nodes if n['tag']=='article' and 'end' in n]
    article = next((n for n in articles if has_class(n,'article')), articles[0] if articles else None)
    if not article:
        return text, {'status':'skipped','reason':'no_article'}
    inside = lambda n: article['start'] < n['start'] < article['end']
    published = sorted(set(day for m in article_metadata(text) if (day := iso_day(m.get('datePublished')))))
    if len(published) > 1:
        return text, {'status':'blocked','reason':'conflicting_publication_dates','dates':published}
    if not published:
        for n in parsed.nodes:
            if n['tag']=='p' and inside(n) and 'end' in n:
                body=text[n['open_end']:n['close_start']]
                match=re.search(r'Published:\s*<time\b[^>]*datetime=["\']([^"\']+)',body,re.I)
                if match and iso_day(match[1]):
                    published.append(iso_day(match[1]))
                    break
    if not published:
        return text, {'status':'blocked','reason':'publication_date_not_recorded'}
    head=next((n for n in parsed.nodes if inside(n) and has_class(n,'article-head') and 'end'in n),None)
    if not head:
        return text, {'status':'blocked','reason':'article_head_not_found'}
    leads=[n for n in parsed.nodes if head['start']<n['start']<head['end'] and has_class(n,'lead') and 'end'in n]
    at=leads[-1]['end'] if leads else head['close_start']
    day=date.fromisoformat(published[0])
    label=f"{day.strftime('%B')} {day.day}, {day.year}"
    byline=f'<p class="byline">By <a href="/about">AniNextUp Editorial Team</a> · Published: <time datetime="{published[0]}">{label}</time> · <a href="/editorial-policy">Editorial policy</a></p>'
    edits=[(n['start'],n['end'],'') for n in parsed.nodes if n['tag']=='p' and inside(n) and has_class(n,'byline') and 'end'in n]
    edits.append((at,at,byline))
    for start,end,value in sorted(edits,key=lambda e:(e[0],e[1]),reverse=True):
        text=text[:start]+value+text[end:]
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text, {'status':'ok','published':published[0]}

def main():
    rows=[]
    for path in sorted((ROOT/'articles').glob('*.html')):
        before=path.read_text(encoding='utf-8')
        after, row=normalize(before)
        row['path']=path.relative_to(ROOT).as_posix()
        row['changed']=after!=before
        if after!=before:
            path.write_text(after,encoding='utf-8')
        rows.append(row)
    report={'articles':len(rows),'changed':sum(r['changed'] for r in rows),'standardized':sum(r['status']=='ok' for r in rows),'unresolved':[r for r in rows if r['status']=='blocked'],'records':rows}
    target=ROOT/'reports'/'article-bylines.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False))
    if report['unresolved']:
        raise SystemExit('Some original dates or article headers require verification; see reports/article-bylines.json')

if __name__=='__main__':
    main()
