#!/usr/bin/env python3
"""Optional OpenAI editorial reviewer. Never publishes or changes files."""
import json
import os
import re
import sys
import urllib.request

def review(title, source_url, verified_text):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY missing; no AI request made")
    if len(verified_text.strip()) < 700:
        raise ValueError("Insufficient official source text")
    model = os.getenv("ANINEXTUP_OPENAI_MODEL", "gpt-4.1-mini")
    prompt = (
        "You are an anime news editor. Only use the supplied official-source text. "
        "Never invent release dates, platforms, episodes, quotes, or corroboration. "
        "Do not copy large passages verbatim. If the source is insufficient, set publish=false. "
        "Return a JSON object with keys publish (boolean), headline (string), "
        "summary (string), article (string), verification_notes (string). "
        "The article must be original English prose with at least five substantive sentences. "
        "Clearly attribute all claims to the official source. "
        "No markdown or HTML.\n"
        + json.dumps({"title": title, "source": source_url, "official_text": verified_text[:12000]}, ensure_ascii=False)
    )
    payload = json.dumps({"model": model, "input": prompt, "text": {"format": {"type": "json_object"}}, "store": False}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=payload,
        headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                 "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=90) as res:
        response = json.load(res)
    blocks = [part.get("text", "") for item in response.get("output", [])
              for part in item.get("content", []) if part.get("type") == "output_text"]
    result = json.loads("".join(blocks))
    if not isinstance(result, dict) or not all(k in result for k in ("publish", "headline", "summary", "article", "verification_notes")):
        raise ValueError("Unexpected AI response")
    if type(result["publish"]) is not bool or any(not isinstance(result[k], str) for k in ("headline", "summary", "article", "verification_notes")):
        raise ValueError("Invalid AI response types")
    if result["publish"] and (len(result["article"]) < 600 or len(re.findall(r"[.!?](?:\\s|$)", result["article"])) < 5):
        raise ValueError("AI editorial output insufficient")
    return result

def main():
    if os.getenv("ANINEXTUP_DRY_RUN", "1").lower() not in ("1", "true", "yes"):
        raise SystemExit("AI editorial preview only; publishing is not implemented")
    if len(sys.argv) != 4:
        raise SystemExit("Usage: ai_editor.py TITLE SOURCE_URL VERIFIED_TEXT_FILE")
    from pathlib import Path
    text = Path(sys.argv[3]).read_text(encoding="utf-8")
    result = review(sys.argv[1], sys.argv[2], text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
