# October 21, 2026 — release coverage and title review

Status: unpublished proposals. No production publication requested or performed.

## New articles

- ELECEED: April 2027 window verified against the production's October 21 Japanese and English notices. No invented premiere day. Crunchyroll distribution distinguished from region/language availability. Official English-version video q7eT3oVvko4: uploadDate 2026-10-21T02:00:08-07:00; duration 63 seconds.
- Haru to Gen: January 4, 2027 at 21:55 JST on tvk verified against AnimationID's October 21 notice and official on-air section. International streaming not announced in checked sources. Official teaser DFbZN4QYhao: uploadDate 2026-10-20T20:00:13-07:00; duration PT37S as declared by YouTube JSON-LD (the integer lengthSeconds extraction rounded differently). The YouTube date's offset differs from the Japanese announcement date; it is intentionally preserved.
- Both classified as Release News because these reports focus on newly confirmed premiere timing for previously announced adaptations.

## Duplicate review before drafting

Read all 108 published article files, assets/data.js and sitemap.xml. Searched ELECEED / エレキシード / 일렉시드 / Illeksideu and Haru to Gen / ハルとゲン / 70-sai / 70歳. The existing Shangri-La Frontier page merely links Crunchyroll's combined acquisition announcement; it is not an ELECEED article. No Haru match. Open editorial PRs #117 and #34 contain neither subject. PR #82 is an AdSense evidence report. The duplicate script subsequently passes for all five changed article candidates against the 108-article baseline.

## Search-title proposals

Three existing articles retain their URLs, H1, article text, release claims, dates and discovery metadata. Only the HTML title changes, placing the franchise and confirmed window first:

- Ghost of Tsushima: Legends Anime Delayed to 2028 | AniNextUp
- One-Punch Man Season 3 Part 2: January 2027 Release | AniNextUp
- SSS-Class Revival Hunter Anime: January 2027 Release | AniNextUp

See seo-title-proposals-20261021.json for exact before/after values. These are editorial hypotheses, not a ranking by current impressions or proven CTR lifts. Google may generate a different title link.

## Checks completed

- Full publication structure validator: all five changed/new article files pass.
- Complete static preflight: 110 draft-branch article files, zero errors and zero warnings.
- Video date validator: all 110 article files pass.
- Five video schema regression tests and two search-index tests pass.
- All three GitHub checks on commit 46e6eb2d2410633c1951bc12942844d7eca1a0d0 completed successfully.
- Publication workflow's reference/index/sitemap validator passes.
- JavaScript syntax and discovery/navigation regression pass.
- Generated latest-news feed, public search index, crawlable hubs and sitemap include both new articles on this draft branch.
- Official hero files return HTTP 200 with image MIME types and nonzero dimensions: ELECEED official OGP JPEG 1200×630, Haru official key visual PNG 2560×1411. Inspected both images; each depicts its named series. YouTube thumbnail responses could not be decoded as images in this environment; players use the verified official visual rather than a generic fallback. This does not establish permission to republish artwork; ELECEED's website expressly restricts reproduction. Media reuse clearance remains pending before publication.

## Checks remaining

- Preview browser review of article heroes, homepage cards, related cards and narrow layouts.
- Actual trailer playback: browser opened both exact official watch pages. Titles/channels and upload dates match the announcement sources. ELECEED JSON-LD declares PT63S; Haru declares PT37S. Both players remained at time 0, readyState 0, so actual playback is NOT VERIFIED. A displayed watch page or play control is not proof that the video played.
- Search Console: opening the service reaches its public introduction page with a sign-in link. No signed-in property was available. Validation of the uploadDate correction has NOT been requested, and current clicks/impressions/CTR have NOT been read. The earlier 20-page correction was deployed and checked separately; this draft does not alter it.
- Explicit owner publication instruction and all remaining material checks are required before either article or the title edits enter main.


## Follow-up review — October 21, 2026

- Updated this draft branch against production commit e345acdb3ea6b855e5af6056fafddc0672a106ae. Resolved generated-file conflicts by keeping current production and rebuilding from the combined data. The 47 verified video timestamps, Today improvements, and Rakuen/Witch cover repairs are retained.
- Re-read both ELECEED October 21 production announcements successfully over HTTPS. They confirm April 2027, the English-version trailer q7eT3oVvko4 and the worldwide wording; no exact first-episode day is given.
- Preview deployment is now available. ELECEED hero loads at 1200 × 630 and matches the named series. Desktop article has no horizontal overflow.
- Replaced the failing SSS-Class thumbnail in ELECEED's related section with the existing PSYREN article and its local official artwork. Shangri-La Frontier also uses the local official asset, with the verified-artwork marker to preserve the reviewed source.
- Simplified repetitive release caveats and preserved the complete official visual with contain framing. Versioned the two drafts' data script to avoid stale related-card data.
- Fresh checks: 110-article preflight zero errors/warnings; full video timestamp validator passes; five schema tests pass; discovery regression passes; both new article structure validations pass; duplicate review against 108 production articles passes. Existing three article proposals change HTML titles only.
- In the preview, the ELECEED button opens the expected embedded YouTube video, whose declared duration is 63 seconds. Actual video playback remains unverified: currentTime 0, readyState 0. The fallback watch link is present.
- Final updated-preview hero/cards/narrow-layout checks are recorded in the PR body after deployment. Browser review uses a 390 CSS-pixel iframe harness, not physical-device emulation.
- No article has been published. Owner's specific publication instruction is still required by editorial/PUBLICATION_QUALITY_GATE.md. Artwork reuse clearance remains unresolved as previously recorded.
