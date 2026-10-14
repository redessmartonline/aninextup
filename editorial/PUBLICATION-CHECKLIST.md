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

## Mandatory trailer/ending presentation standard
- For any verified embeddable YouTube trailer, opening, or ending, use the existing `.lite-trailer[data-youtube]` component with a `.trailer-play` button containing an image thumbnail and `.trailer-overlay` with the visible play label and video title.
- Never use a plain text-only `.trailer-play` button. The thumbnail, centered play overlay, 16:9 container, and click-to-load player must match other AniNextUp articles.
- Check the exact official video ID, thumbnail loading, and playback before publication. If no verified embeddable video exists, link to the official source instead of inventing an embed.
- Verify mobile and desktop presentation and do not mark the media QA gate complete without checking the published page.

## Mandatory editorial depth and article parity
- Before publication, compare the draft with two recent complete AniNextUp articles for structure and editorial usefulness, not just word count.
- Include a clear release-at-a-glance summary when factual release details exist; explain what changed, why it matters, series context, and where the official media or release can be accessed.
- Use distinct factual H2 sections and primary-source citations. Never pad with unsupported staff, release dates, regions, or invented claims merely to reach a word target.
- Ensure media layout, lead-cover treatment, related content, and SEO metadata match established site patterns.
- If the story lacks enough confirmed substance for a full article, keep it as a brief or draft rather than presenting an underdeveloped article as complete.
