# AniNextUp — Mandatory pre-publication gate

Every new or materially updated article MUST pass these checks **before** asking for final publication approval or merging to `main`.

## Cover: BLOCKING
- [ ] The primary cover depicts the **correct anime** and is appropriate to the specific story. Prefer the most recent relevant official key visual.
- [ ] Record an official publisher/studio/show source page and the direct image URL or a repository-hosted copy with rights and provenance checked.
- [ ] Verify that the direct image returns an actual image (not a 403/404, HTML, placeholder, or hotlink-blocked response) and renders in a browser at desktop and mobile sizes.
- [ ] The article hero, home-page card (`assets/data.js`), and `og:image` use the same verified anime-specific cover.
- [ ] Fallback art may be configured **only** as a runtime failure recovery. Never publish a new article with `anime-image-fallback.svg` as its normal cover.
- [ ] If an image cannot be verified, **STOP**. Keep the article in a draft branch and report the blocker; do not publish, even if the text is ready.

## Editorial and technical
- [ ] Cross-check facts, cast, dates, and staff against official sources; clearly label unconfirmed details.
- [ ] Search `sitemap.xml`, `assets/data.js`, and article paths to prevent duplicate coverage.
- [ ] Verify canonical, SEO title/description, structured data, internal links, related cards, and image fallback behavior.
- [ ] Ensure new stories appear in the homepage news index and are added to `sitemap.xml` upon approval.
- [ ] Obtain explicit user approval **after** the cover and all blocking checks pass.
- [ ] After merge, verify the public URL, homepage card, mobile and desktop image loading. If deployment cannot be confirmed, report that separately instead of claiming the public website was verified.

## Review record
Each publication PR should record the cover source, direct cover URL, duplicate check, visual test outcome, and any outstanding nonblocking checks. Do not mark the PR publication-ready with an unresolved blocking item.

## Mandatory cover and media verification (October 2026)
- Both exterior and interior covers must show verified official artwork specifically related to the article, not placeholders.
- Verify image URLs return real image content and confirm intrinsic resolution and suitable 16:9 cropping; `maxresdefault.jpg` is not automatically a valid high-resolution image.
- Verify the actual video ID and that playback works on the published article.
- Do not merge or publish when these checks fail; keep the story as a draft.
- Existing Paw & Palaces publication is an exception requiring follow-up: high-resolution YouTube thumbnail availability and live playback have NOT been verified.
