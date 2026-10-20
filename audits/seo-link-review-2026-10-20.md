# AniNextUp — SEO and link review, October 20, 2026

## Changes

- Resolved the 18 findings from the publication SEO validator without changing its rules: six missing BreadcrumbList schemas, five missing VideoObject schemas, two guides with multiple primary players, and the Chihara-san index mismatch.
- Retained one primary trailer in Bass X Machina and Magic Knight Rayearth. Supplementary official videos remain available through labelled YouTube links.
- Merged the duplicate Chihara-san index entry, retaining its confirmed premiere date and category. Its article metadata now identifies it as the same anime release as the central index.
- Corrected the broken Cyberpunk Netflix link from title 81744226 to the current series listing, title 81054853, verified on Netflix.
- Added contextual links from Cyberpunk, Made in Abyss, Maebashi Witches and My Happy Marriage to Today, This Week and the November release guide as appropriate.
- Added a nonduplicate Shangri-La Frontier Season 3 guide with official production artwork, January 10, 2027 Japanese premiere, two-cour announcement, production credits and the October 15 official exhibition interview. The interview is explicitly identified as an interview, not a trailer.
- Browser verification exposed a separate discovery-cache issue: the unversioned release index was cached for a day. Discovery generation now adds a content-derived version to every root-page index script, and static News cards use the same category selection as the browser. Regression checks cover both behaviors.

## Verification

- Publication reference and SEO validation: passes for all 107 article files.
- Static article preflight: 107 articles, zero errors and zero warnings.
- Duplicate review: changed article candidates compared against all 106 previously published articles; passes.
- Discovery/navigation regression: passes, including date boundaries, prerendered hubs and related article targets.
- JavaScript syntax, sitemap XML, metadata JSON and whitespace checks: pass.
- Baseline internal-reference scan: 121 public HTML pages, 2,592 local links and 633 asset references; no missing repository targets. This validates clean URLs against their HTML targets and assets against the full remote tree.
- All article pages contain a viewport declaration. Responsive article/related-card CSS remains in place. A real mobile viewport was not available in this browser session; static responsive checks are not a substitute for a mobile visual test.

## External-resource audit

GitHub Actions public-resource audit for commit 1a676b72e1e53b428a992a18e26dde5b5a2a6ff6, completed October 20 at approximately 12:29 UTC, scanned 558 external resources: 551 accessible, one confirmed broken link, six indeterminate links. All 142 image references were accessible. All 76 YouTube metadata checks were accessible; this does not verify video playback or territorial availability.

The broken Netflix link is corrected in this change. The following six resources were left intact because a timeout or access restriction is not evidence of a dead link:

- Netflix Media Center title 81663323: timeout.
- Comic Natalie news 654890: HTTP 405.
- X account BokenshaLicense: HTTP 403.
- Seven Seas Chihara-san series page: HTTP 403.
- Sony Music Ghost of Tsushima production announcement: HTTP 403.
- Pro Game Guides Anime Mysterious codes page: HTTP 403.

## Existing test limitations

The existing related-grid and progressive-search unit tests and one publisher-safety test fail identically on the untouched baseline and this change. These tests contain expectations or mocks that do not match existing implementation. They were not weakened or presented as passing. The related-cover test additionally requires binary assets not materialized in the local text checkout; its local run is inconclusive.

This review resolves the enumerated publication findings. It does not guarantee Google indexing, rankings, rich-result eligibility or increased traffic.
