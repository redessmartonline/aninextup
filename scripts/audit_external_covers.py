#!/usr/bin/env python3
"""Audit every external cover in assets/data.js; never modify site content."""
import ast
import collections
import io
import json
import pathlib
import re
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from PIL import Image, UnidentifiedImageError

root = pathlib.Path(__file__).resolve().parents[1]
source = (root / "assets/data.js").read_text(encoding="utf-8")
rows = []
for line in source.splitlines():
    if not re.search(r'\bid:"', line):
        continue
    def field(name):
        m = re.search(r'\b' + name + r':("(?:\\.|[^"\\])*"|null)', line)
        return ast.literal_eval(m.group(1)) if m and m.group(1) != "null" else None
    ident, url = field("id"), field("image")
    if ident and url and url.startswith(("https://", "http://")):
        rows.append((ident, url))
results = []
for ident, url in rows:
    entry = {"id": ident, "url": url, "status": "unverified", "http_status": None,
             "content_type": None, "bytes": 0, "format": None, "dimensions": None}
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; AniNextUpCoverAudit/1.0)",
                                    "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"})
        with urlopen(req, timeout=25) as response:
            entry["http_status"] = response.status
            entry["content_type"] = response.headers.get("Content-Type", "").split(";")[0].lower()
            raw = response.read(15 * 1024 * 1024 + 1)
            entry["bytes"] = len(raw)
            if len(raw) > 15 * 1024 * 1024:
                entry["status"] = "too_large"
            else:
                try:
                    img = Image.open(io.BytesIO(raw))
                    entry["format"] = img.format
                    entry["dimensions"] = list(img.size)
                    img.verify()
                    entry["status"] = "ok" if entry["content_type"].startswith("image/") else "image_wrong_content_type"
                except (UnidentifiedImageError, OSError, ValueError) as error:
                    entry["status"] = "invalid_image"
                    entry["detail"] = str(error)[:160]
    except HTTPError as error:
        entry["http_status"] = error.code
        entry["status"] = "http_error"
        entry["detail"] = str(error.reason)[:160]
    except (URLError, TimeoutError, ConnectionError, OSError) as error:
        entry["status"] = "network_error"
        entry["detail"] = str(error)[:160]
    results.append(entry)
    print(f"{ident}: {entry['status']} HTTP={entry['http_status']} type={entry['content_type']} format={entry['format']}", flush=True)
    time.sleep(0.2)
summary = dict(collections.Counter(item["status"] for item in results))
report = {"generated_utc": datetime.now(timezone.utc).isoformat(),
          "scope": "External cover images referenced by assets/data.js",
          "note": "403/429/network errors can be anti-bot restrictions; do not automatically replace images.",
          "total": len(results), "summary": summary, "images": results}
out = root / "cover_http_audit.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
lines = ["# AniNextUp external cover HTTP audit", "", f"Checked: {len(results)}", "",
         "| ID | HTTP | MIME | Format | Size | Result |", "|---|---:|---|---|---|---|"]
for x in results:
    lines.append(f"| {x['id']} | {x['http_status'] or '-'} | {x['content_type'] or '-'} | {x['format'] or '-'} | {x['dimensions'] or '-'} | {x['status']} |")
(root / "cover_http_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"total": len(results), "summary": summary}), flush=True)
