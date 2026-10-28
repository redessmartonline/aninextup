# AniNextUp — Mandatory pre-publication gate

## New-article standard — owner instruction, October 28, 2026

This standard applies to articles created after this instruction. It supersedes earlier 800–1,000-word targets for NEW articles; it does not require bulk expansion of existing articles.

- Write **1,200–2,000 words of original English main editorial content**. Count the lead and substantive article text, excluding navigation, metadata, source lists, captions, repeated table labels, related cards and footer.
- Before drafting, identify one primary user search intent, one primary keyword cluster and relevant secondary questions. Use current Search Console signals when available; do not invent search volumes, difficulty scores or ranking forecasts.
- Search existing canonical articles, aliases and open editorial work first. Update an existing page when it serves the same intent rather than create competing duplicate pages.
- Answer the main question directly in the opening. Organize useful H2/H3 sections around actual reader questions, not a repeated template or a fixed keyword density.
- Cover relevant release dates, exact versus year/month-only windows, platforms, countries, language versions, episode information, watch order and story context ONLY when those questions fit the topic and the evidence supports the answers. State unknowns clearly.
- Add original editorial value through source comparison, clear release-scope distinctions, useful tables or explanations; distinguish interpretation from confirmed facts. Never add filler, repeated paragraphs, invented FAQs or unsupported claims to reach the range. If the evidence cannot support 1,200 useful words, choose a better-supported topic or update an existing guide; flag the shortfall instead of publishing it as compliant.
- Use a concise, descriptive SEO title and unique description, one H1, clear headings, a preserved canonical URL and accurate structured data. Place keywords naturally; avoid stuffing, clickbait and unsupported promises.
- Add relevant contextual internal links and exactly three related cards with real destination artwork. Keep the verified official cover and embed an official trailer whenever one is available.
- Record the word count, primary intent, target keyword cluster, questions answered, sources and verification limits in the editorial review record.
- Validate factual accuracy, useful answers, images, video, links, metadata, index/sitemap inclusion and deployed rendering. Assess Search Console impressions, clicks, CTR and position after recrawling; length and SEO edits do not guarantee Google rankings.

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

## Official trailers: required whenever available (October 27, 2026)
- Search the official announcement and show media page for the relevant trailer, teaser or season announcement video for every release article, even when the headline does not mention a video.
- When a relevant official video is available, include the in-page `.lite-trailer` player with a thumbnail and play button. Do not substitute a description of the video or an outbound-only YouTube link for playback.
- Record `trailer.youtubeId`, `title`, `sourceUrl`, `thumbnail` and `verifiedOn` in `aninextup-index`. The video validator blocks a recorded available trailer if its player is missing, mismatched or outbound-only.
- Verify the source, exact installment, image and live playback. If embedding is restricted, report the actual restriction; do not silently omit the available video or claim in-page playback works.
- VideoObject markup requires a verified upload timestamp. Omit that optional markup when its metadata cannot be verified; keep the verified player. Never invent an upload date or remove a working trailer solely because its SEO metadata is incomplete.
