# Outstanding media and external-resource verification — 2026-10-16

This report uses the **actual ZIP artifact** from the successful AniNextUp Public Resource Audit workflow #38942578081 (artifact #12062779293), not just its job's summary. The artifact's `results.json` was inspected. Scope: **88 article HTML files**. This does **not** certify factual accuracy, copyright permissions, YouTube playback or AdSense approval.

## Four exact indeterminate resources

| URL | Reported result | Referenced by | Independent follow-up | Disposition |
| --- | --- | --- | --- | --- |
| https://about.netflix.com/ja/news/anime-nyc-2026 | TimeoutError (no HTTP code) | anime-releasing-november-2026, bass-x-machina-release-date, fall-2026-anime-calendar, fool-night-release-date, netflix-october-2026 | Netflix's official August 21, 2026 newsroom release was retrievable through an independent web lookup and confirms its event announcement; the source includes the November 26 Fool Night and November 3 Bass X Machina announcements. | **Not a dead link.** Timeout from CI remains an environment-specific indeterminate result; retain the official URL. |
| https://www.sonymusic.com/sonymusic/crunchyroll-aniplex-sme-and-playstation-productions-to-produce-anime-ghost-of-tsushima-legends/ | HTTP 403 | ghost-of-tsushima-legends-anime-2028 | Sony Music's original January 6, 2025 announcement was retrievable through independent web search, identifying the production partners and initial 2027 plan. Newer Crunchyroll announcement in earlier audits supersedes the old release year with 2028. | **Not proven broken.** The CI client received a 403; do not delete the historical source. |
| https://natalie.mu/comic/news/654890 | HTTP 405 | i-lost-my-adventurers-license-anime-january-2027 | No independent content-level verification completed for this exact URL in this batch. The official production website is separately cited and previously checked for January 2027. | **Still indeterminate**, not confirmed 404/410. Do not invent replacement URL. |
| https://x.com/BokenshaLicense | HTTP 403 | i-lost-my-adventurers-license-anime-january-2027 | Social media commonly restricts automated clients; account authenticity, login visibility and current content have not been checked through an authenticated browser. | **Still indeterminate**, not confirmed broken. |

## Current automated results

- 440 external references: **436 accessible, 0 confirmed broken, 4 indeterminate**.
- 115 image references in the external-resource report; HTTP accessibility **does not establish permission to republish**.
- 64 unique YouTube IDs: 64 accessible oEmbed metadata results, 0 metadata failures. **No actual playback or region test** was performed.
- Existing static all-articles preflight reports 88 articles, 0 structural errors, 0 warnings; release-entry editorial schema audit reports 49/49, 0 warnings. These do **not** verify factual claims.

## Added executable inventory

Run `python3 scripts/build_media_rights_playback_queue.py` in the repository. It scans **every article HTML file**, and writes three CSV files under `audits/generated/`:

1. `media-image-rights-queue.csv`: article, image URL, alt, external hosting, license evidence and permission status.
2. `media-video-playback-queue.csv`: article, video ID, official provenance, real-browser playback, tested region and notes.
3. `editorial-manual-completion-queue.csv`: article-level factual, rights and playback completion flags.

**The script deliberately defaults every rights decision to UNVERIFIED, every playback result to NOT_TESTED, and every full-article completion flag to NO.** It cannot grant licenses, prove video playback, or compare factual claims with official sources. No empty checkbox should be interpreted as a pass.

## Remaining blockers to an honest all-clear

- Claim-by-claim source comparisons for the remaining article assertions.
- Written permissions, qualifying press-use terms or other applicable legal basis for external imagery; remove or replace only material that is demonstrably unauthorized and for which a lawful alternative is available.
- A real interactive browser test of each relevant player and country/consent condition.
- Manual authenticated/browser review for the Comic Natalie and X links if those remain important editorial citations.
- Google AdSense approval is determined by Google, not by local workflow success.

**No public article, image, trailer, design, search UI or disabled workflow has been modified by this PR.**
