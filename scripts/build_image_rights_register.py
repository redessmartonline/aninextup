#!/usr/bin/env python3
"""Inventory image provenance separately from manually documented reuse rights.

No source URL, copyright notice or successful download grants a license.
Permission decisions live in audits/media-permissions.json and survive rebuilds.
"""
import csv
import json
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://aninextup.com/"

def asset_key(src, article):
    url = urlsplit(urljoin(SITE + article, src))
    if url.hostname in ("aninextup.com", "www.aninextup.com"):
        return url.path
    return url.geturl()

class ArticleImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.figure = None
        self.caption = False
        self.caption_text = []
        self.caption_links = []
        self.caption_tag = None
        self.caption_targets = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "figure":
            self.figure = []
            self.caption_text, self.caption_links = [], []
        if tag == "figcaption" or (tag == "p" and any(x in a.get("class", "").split() for x in ("image-caption", "image-credit", "hero-caption", "caption"))):
            self.caption = True
            self.caption_tag = tag
            self.caption_targets = self.figure if self.figure is not None else self.images[-1:]
            self.caption_text, self.caption_links = [], []
        if tag == "a" and self.caption and a.get("href", "").startswith("https://"):
            self.caption_links.append(a["href"])
        if tag == "img" and (a.get("src") or a.get("data-src")):
            item = {"src": a.get("src") or a["data-src"], "alt": a.get("alt", ""), "credit": "", "credit_links": []}
            self.images.append(item)
            if self.figure is not None:
                self.figure.append(item)
    def handle_data(self, data):
        if self.caption:
            self.caption_text.append(data)
    def handle_endtag(self, tag):
        if tag == self.caption_tag and self.caption:
            self.caption = False
            for image in self.caption_targets:
                image["credit"] = " ".join("".join(self.caption_text).split())
                image["credit_links"] = self.caption_links[:]
            self.caption_tag = None
        if tag == "figure" and self.figure is not None:
            self.figure = None

def build(root=ROOT):
    records = {}
    def record(key):
        return records.setdefault(key, {"asset": key, "articles": [], "alt_texts": [], "provenance": [], "published_credits": []})
    for article in sorted((root / "articles").glob("*.html")):
        path = article.relative_to(root).as_posix()
        parser = ArticleImages()
        parser.feed(article.read_text(encoding="utf-8"))
        for image in parser.images:
            item = record(asset_key(image["src"], path))
            if path not in item["articles"]:
                item["articles"].append(path)
            if image["alt"] and image["alt"] not in item["alt_texts"]:
                item["alt_texts"].append(image["alt"])
            if image["credit"]:
                credit = {"article": path, "text": image["credit"], "links": image["credit_links"]}
                if credit not in item["published_credits"]:
                    item["published_credits"].append(credit)
    manifest_path = root / "assets/images/external/sources.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for source in manifest.get("images", []):
        key = asset_key(source["local"], "")
        if key not in records:
            continue
        url = source.get("source", "")
        if urlsplit(url).hostname in ("aninextup.com", "www.aninextup.com"):
            continue  # A local self-reference does not identify the original supplier.
        evidence = {"source_asset_url": url, "evidence_type": "repository_download_history", "evidence_commit": source.get("evidence_commit", "")}
        if source.get("download_url") and source["download_url"] != url:
            evidence["download_url"] = source["download_url"]
        if evidence not in records[key]["provenance"]:
            records[key]["provenance"].append(evidence)
    covers_path = root / "assets/images/covers/related-cover-sources.json"
    if covers_path.exists():
        for asset, source in json.loads(covers_path.read_text()).items():
            key = asset_key(asset, "")
            if key in records:
                records[key]["provenance"].append({"source_page": source.get("source_page", ""), "source_asset_url": source.get("asset_url", ""), "credit": source.get("credit", ""), "evidence_type": "existing_asset_source_record"})
    maintenance_path = root / "reports/first-maintenance-cover-sources-20261021.json"
    if maintenance_path.exists():
        for source in json.loads(maintenance_path.read_text()):
            key = asset_key(source["localAsset"], "")
            if key in records:
                records[key]["provenance"].append({"source_asset_url": source["source"], "evidence_type": "existing_download_report"})
    permissions_path = root / "audits/media-permissions.json"
    permissions = json.loads(permissions_path.read_text()) if permissions_path.exists() else {"assets": {}}
    for key, item in records.items():
        reviewed = permissions.get("assets", {}).get(key, {})
        item["permission_status"] = reviewed.get("permission_status", "UNVERIFIED")
        item["rights_holder"] = reviewed.get("rights_holder")
        item["rights_holder_evidence"] = reviewed.get("rights_holder_evidence", [])
        item["license_evidence"] = reviewed.get("license_evidence", [])
        item["permission_scope"] = reviewed.get("permission_scope", "")
        item["review_notes"] = reviewed.get("review_notes", "No asset-specific reuse authorization established by this inventory.")
        if item["permission_status"] == "DOCUMENTED_PERMISSION" and not (item["license_evidence"] and item["permission_scope"] and item["rights_holder"]):
            raise ValueError("Permission requires a holder, scope and evidence: " + key)
    return sorted(records.values(), key=lambda x: x["asset"])

def main():
    records = build()
    out = ROOT / "audits/generated"
    out.mkdir(parents=True, exist_ok=True)
    summary = {"scope": "Distinct img/src or img/data-src references in article HTML; relative paths normalized. Not an inventory of CSS, social metadata or non-article pages.", "unique_assets": len(records), "with_download_provenance": sum(bool(x["provenance"]) for x in records), "with_published_credit": sum(bool(x["published_credits"]) for x in records), "documented_permissions": sum(x["permission_status"] == "DOCUMENTED_PERMISSION" for x in records)}
    (out / "media-rights-register.json").write_text(json.dumps({"summary": summary, "assets": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "media-rights-register.csv").open("w", encoding="utf-8", newline="") as fp:
        fields = ["asset", "article_count", "source_asset_urls", "source_pages", "published_credit", "rights_holder", "permission_status", "license_evidence", "permission_scope", "review_notes"]
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for item in records:
            writer.writerow({"asset": item["asset"], "article_count": len(item["articles"]), "source_asset_urls": " | ".join(sorted({x["source_asset_url"] for x in item["provenance"] if x.get("source_asset_url")})), "source_pages": " | ".join(sorted({link for x in item["published_credits"] for link in x["links"]})), "published_credit": " | ".join(sorted({x["text"] for x in item["published_credits"]})), "rights_holder": item["rights_holder"], "permission_status": item["permission_status"], "license_evidence": json.dumps(item["license_evidence"], ensure_ascii=False), "permission_scope": item["permission_scope"], "review_notes": item["review_notes"]})
    print(json.dumps(summary))

if __name__ == "__main__":
    main()
