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
