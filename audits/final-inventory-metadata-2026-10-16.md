# AniNextUp — final inventory and metadata audit (2026-10-16)

Scope: read-only checks against the 88 article HTML files on GitHub main, plus sitemap and repository tree. This is **not** an HTTP crawl or independent factual verification.

## Confirmed checks

- Article HTML files: **88**.
- Sitemap URLs: **101**; article URLs: **88**.
- Missing article sitemap entries: **0**.
- Sitemap article URLs without corresponding article files: **0**.
- Duplicate sitemap URLs: **0**.
- Essential files present: `robots.txt`, `ads.txt`, `sitemap.xml`, `about.html`, `contact.html`, `privacy.html`, `terms.html`, `editorial-policy.html`.
- All 88 articles were individually fetched and screened for a nonempty HTML title, meta description, canonical, JSON-LD presence, parseable JSON-LD blocks, and a `dateModified` field.
- **One missing `dateModified`** detected in `articles/full-clearing-another-world-zero-believers-premiere.html`. This branch adds it to the NewsArticle JSON-LD, preserving the original `datePublished`.
- No other missing fields or JSON-LD parsing errors were detected by this specific screening.

## Outstanding verification — do not interpret as passed

1. Full internal-link and local-image resolution across all pages; external link HTTP status, redirects, image content and license.
2. Trailer availability, embed playback and regional restrictions.
3. Independent article-by-article factual verification against official announcements.
4. Near-duplicate prose assessment, thin content and originality assessment.
5. Public deployment, Search Console indexing, Core Web Vitals, AdSense approval and consent implementation.

## Reproducible project tools

- `python scripts/editorial_audit.py` — structural check against entries in `assets/data.js`.
- `python scripts/audit_adsense_readiness.py` — local links, images, titles, sitemap and site essentials.
- `python scripts/audit_public.py` — live resource status and similarity screening; external failures may be indeterminate.
- `python scripts/audit_public_resources.py` — external image and video metadata audit; does not prove video playback.

These scripts have been inspected, but **not executed in this audit session**. Their earlier reports must not be presented as fresh results.
