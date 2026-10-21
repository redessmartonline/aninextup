# PR #117 — article preparation and verification

Date: October 20, 2026. Status: UNPUBLISHED; visual/media gate incomplete.

## Completed
- Two complete English HTML articles built from the existing Nue's Exorcist / The Fable article structure.
- Header, breadcrumb, lead, byline, official hero/caption, Release at a glance, factual H2 sections, corrections links and footer.
- Each has exactly two established related cards, using the previously verified local January guide / Hasunosora artwork.
- NewsArticle, BreadcrumbList, canonical, OpenGraph, Twitter and matching central index data.
- News taxonomy: Prisma Illya = Returning Series; True Saint = New Anime.
- Proposed sitemap and search aliases added on this editorial branch only.
- True Saint teaser ID AgwEj6-rVdw is linked by its official October 3 announcement. Added the standard lite-trailer with thumbnail, overlay, YouTube fallback and matching VideoObject.
- Corrected character-design romanization to Naru Nishikori and manga credit to Mokuba Matsu.
- No verified FINALE-specific video located in the inspected official page; official source link retained rather than substituting an older film's trailer.

## Media provenance and evidence
Prisma Illya source: https://anime.prisma-illya.jp/finale/
Hero / social image: https://anime.prisma-illya.jp/finale/img/ogp.jpg
The official site's OpenGraph specifies that exact image. Read-only extraction opened it as an image document titled "ogp.jpg (1200×630)" without extraction error.

True Saint source: https://www.shinnoseijo-anime.com/
Hero / social image: https://www.shinnoseijo-anime.com/assets/img/ogp.png
The official site's OpenGraph specifies the image. Read-only extraction followed the bare-domain URL to the www URL and returned an image document titled "ogp.png (1200×630)" without extraction error.
Teaser source: https://www.shinnoseijo-anime.com/news/detail.php?id=25837
Its actual iframe target contains AgwEj6-rVdw, matching the proposed component.

This establishes official provenance, address and nonzero reported image-document dimensions. It does NOT establish HTTP MIME/status independently, visual subject inspection, final card crop or playback. Publication artwork checks remain incomplete.

## Checks
- In-session JavaScript inspection: JSON metadata parseability, expected HTML components, two related cards, balanced containers, consistent image/title/index fields.
- Added scoped GitHub Actions validation using the repository's existing publication validator, duplicate detector and all-article preflight audit. Results must be checked on the PR; do not describe queued checks as passed.
- No local Python/build/browser environment is available, so local execution was not claimed.

## Remaining blocking items
- Real desktop and mobile rendering of article hero, proposed homepage card and related cards; verify no fallback or subject/crop error.
- Independent image response MIME/status and actual browser subject identity.
- True Saint thumbnail rendering and actual click-to-play success.
- Verify any later discovered FINALE trailer against the correct production.
- Confirm PR automated checks complete successfully.
- After eventual publication authorization, generate/refresh discovery HTML and search index, then verify live URLs.

## Cost constraint
A read-only TinyFish browser automation for media QA was rejected by automatic approval review because it consumes credits and the owner requested no paid tools. No paid browser run was executed; no alternative was used to bypass the rejection.

Keep PR #117 as a draft. The branch has proposed publication assets, but production main has not been changed.


## October 21 free-browser review update

The public branch preview URL was recovered from Cloudflare's PR comment, so preview inspection no longer requires dashboard authentication. A dashboard sign-in attempt returned 403 and was not repeated.

Verified in the actual branch preview:
- Both official hero images display the correct named series and load at 1200 x 630. Independent image requests returned 200 image/jpeg and 200 image/png.
- Both articles render at desktop width without horizontal overflow.
- The noindex responsive review harness embeds a 390 CSS pixel frame (375 pixel content width with scrollbar). Both articles fit that content width without horizontal overflow. This is a responsive frame test, not a physical-mobile-device test.
- All three runtime related cards load their correct images; the two authored cards and the existing application's third recommendation remain one row.
- Discovered a broken YouTube thumbnail (naturalWidth 0). Fixed the lite-trailer poster and VideoObject thumbnailUrl to the verified official True Saint artwork; both corrected images now load at 1200 x 630.
- The standard button loads the correct youtube-nocookie iframe, title and official channel. Actual media playback does NOT advance: currentTime stays 0 and readyState stays 0. This occurs on the production's own official embed too. Do not label playback passed.
- Regenerated proposed homepage/news HTML, latest-news feed and the full 110-article search index. Both new stories are in the first seven homepage items.
- Local existing publication validator passes both articles; discovery test passes. GitHub checks and branch deployment passed after the poster fix.

Remaining: inspect regenerated homepage cards after preview deployment, record final CI status, and verify actual teaser playback when this browser can load the media. Production main remains unchanged; the PR is not ready for unconditional publication while playback remains unverified.
