# Remaining two social preview images — 2026-10-16

## Scope
This patch changes **only** `og:image` and `twitter:image` metadata in two articles. It does not change the article's visible image, HTML body, layout, existing trailers, or `assets/data.js`.

## Image selection: reuse existing AniNextUp image references
- `articles/bass-x-machina-release-date.html`: `https://i.ytimg.com/vi/CWbZBIrEfqI/hqdefault.jpg`. Already used in the AniNextUp `assets/data.js` listing for this article and the article's existing official Netflix teaser `VideoObject`. Netflix confirms its November 3, 2026 date and teaser: https://about.netflix.com/ja/news/anime-nyc-2026 and https://about.netflix.com/en/news/netflix-unveils-upcoming-anime-slate-out-of-annecy-festival.
- `articles/manchuria-opium-squad-anime.html`: `https://i0.wp.com/anitrendz.net/news/wp-content/uploads/2026/10/Manchuria-Opium-SquadFirst-Anime-Adaptation-Visual-EN.jpg?ssl=1`. Already used by AniNextUp `assets/data.js` for the same article. Official adaptation announcement and anime announcement visual: https://news.ponycanyon.co.jp/2026/10/126491.

## Important outstanding checks
- **No image copyright license is asserted.** The fact that these URLs already appear on the site's homepage data is not permission to reuse them. The Manchuria URL is hosted by a third party rather than the official rights holder; obtain authorization or replace with a properly licensed image if necessary.
- External hosts may reject social crawler requests, return different images, or change their URLs. Browser/social crawler rendering and image HTTP status were not validated by this metadata-only patch.
- The 88-article static preflight should drop from 2 warnings to **0 warnings** if the workflow executes successfully; this is an expectation, not a claim of a completed run.
- This patch does not establish AdSense approval, editorial fact checking for all articles, or image usage rights.
