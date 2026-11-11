#!/usr/bin/env python3
"""Evidence-first editorial similarity and image provenance inventory.

A similarity flag is not a plagiarism finding. An image URL is not a license.
"""
import csv, html, re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"audits"/"generated"
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(); self.article=0; self.ignore=0; self.parts=[]; self.paragraphs=[]; self.images=[]; self.current=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="article": self.article+=1
        if tag in ("script","style","nav","footer"): self.ignore+=1
        if tag=="p" and self.article: self.current=[]
        if tag=="img" and self.article:
            src=a.get("src") or a.get("data-src") or ""
            if src: self.images.append((src,a.get("alt","")))
    def handle_endtag(self,tag):
        if tag=="p" and self.current is not None:
            self.paragraphs.append(" ".join(self.current).strip()); self.current=None
        if tag=="article": self.article=max(0,self.article-1)
        if tag in ("script","style","nav","footer"): self.ignore=max(0,self.ignore-1)
    def handle_data(self,data):
        if self.article and not self.ignore:
            self.parts.append(data)
            if self.current is not None: self.current.append(data)
def words(s): return re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*",html.unescape(s).lower())
def grams(s,n=7):
    w=words(s)
    return set(tuple(w[i:i+n]) for i in range(max(0,len(w)-n+1)))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    pages=[]; image_rows=[]; repeated=defaultdict(set)
    for path in sorted((ROOT/"articles").glob("*.html")):
        p=Reader(); p.feed(path.read_text(encoding="utf8",errors="replace"))
        name=path.relative_to(ROOT).as_posix()
        body=" ".join(p.parts)
        paragraphs=[re.sub(r"\s+"," ",x).strip() for x in p.paragraphs if len(words(x))>=18]
        for para in paragraphs: repeated[tuple(words(para))].add(name)
        pages.append({"article":name,"words":len(words(body)),"paragraphs":len(paragraphs),"grams":grams(body),"images":len(p.images)})
        for src,alt in sorted(set(p.images)):
            host=urlsplit(src).hostname or ""
            image_rows.append({"article":name,"image_url":src,"alt":alt,"host":host,"external":bool(host and host not in ("aninextup.com","www.aninextup.com")),"reuse_permission":"UNVERIFIED","license_evidence":"","action":"REVIEW_PERMISSION_OR_REPLACE","review_notes":""})
    similarity=[]
    for i,a in enumerate(pages):
        for b in pages[i+1:]:
            common=len(a["grams"]&b["grams"])
            ratio=common/max(1,min(len(a["grams"]),len(b["grams"])))
            if ratio>=0.25 and common>=15:
                similarity.append({"article_a":a["article"],"article_b":b["article"],"shared_7grams":common,"overlap_of_shorter":round(ratio,3),"decision":"HUMAN_REVIEW_REQUIRED"})
    duplicates=[{"article":name,"other_articles":" | ".join(sorted(members-{name})),"paragraph_excerpt":" ".join(para)[:220]} for para,members in repeated.items() if len(members)>1 for name in sorted(members)]
    def write(name,rows,fields):
        with (OUT/name).open("w",encoding="utf8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    write("editorial-similarity-pairs.csv",sorted(similarity,key=lambda r:-r["overlap_of_shorter"]),["article_a","article_b","shared_7grams","overlap_of_shorter","decision"])
    write("editorial-identical-paragraphs.csv",duplicates,["article","other_articles","paragraph_excerpt"])
    write("editorial-article-lengths.csv",[{"article":p["article"],"article_words":p["words"],"paragraphs":p["paragraphs"],"review_priority":"CHECK_DEPTH" if p["words"]<250 else "NORMAL"} for p in pages],["article","article_words","paragraphs","review_priority"])
    write("adsense-image-rights-evidence.csv",image_rows,["article","image_url","alt","host","external","reuse_permission","license_evidence","action","review_notes"])
    print(f"ARTICLES={len(pages)} SIMILAR_PAIRS={len(similarity)} IDENTICAL_PARAGRAPH_OCCURRENCES={len(duplicates)} IMAGE_OCCURRENCES={len(image_rows)}")
    print("Signals are screening only. Permission cannot be inferred from image hosting, credits or accessibility.")
if __name__=="__main__": main()
