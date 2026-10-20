#!/usr/bin/env python3
"""Build one public article-search index; exclude navigation and related cards."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class ArticleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.heading=[]
        self.words=[]
        self.description=''
        self.canonical=''
        self.indexable=True

    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name','').lower()=='description':self.description=a.get('content','')
        if tag=='meta' and a.get('name','').lower()=='robots' and 'noindex' in a.get('content','').lower():self.indexable=False
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href','')
        parent=self.stack[-1] if self.stack else ('',False,False,False)
        ignored=parent[1] or tag in {'script','style','nav','footer'} or 'related-releases' in a.get('class','').split() or (tag=='header' and 'site-header' in a.get('class','').split())
        article=parent[2] or tag=='article'
        heading=parent[3] or tag=='h1'
        if tag not in VOID:self.stack.append((tag,ignored,article,heading))

    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]
                break

    def handle_data(self,data):
        if not self.stack:return
        _,ignored,article,heading=self.stack[-1]
        if ignored:return
        if heading:self.heading.append(data)
        if article:self.words.append(data)

def build(root=ROOT):
    alias_path=root/'assets/search-aliases.json'
    aliases=json.loads(alias_path.read_text()) if alias_path.exists() else {}
    rows=[]
    for path in sorted((root/'articles').glob('*.html')):
        page=ArticleText();page.feed(path.read_text(encoding='utf-8'))
        canonical=urlsplit(page.canonical)
        expected='/articles/'+path.stem
        title=' '.join(' '.join(page.heading).split())
        if not page.indexable or not title or canonical.scheme!='https' or canonical.netloc!='aninextup.com' or canonical.path!=expected:continue
        rows.append({'title':title,'description':page.description,'url':expected,'aliases':aliases.get(expected,[]),'content':' '.join(' '.join(page.words).split())})
    return {'version':1,'entries':rows}

if __name__=='__main__':
    result=build()
    out=ROOT/'assets/search-index.json'
    out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(f"Search index: {len(result['entries'])} public articles; {out.stat().st_size} bytes")
