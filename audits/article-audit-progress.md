# AniNextUp — article audit status

Updated 2026-10-16. **Current repository inventory: 88 published article HTML files**, not 59. This page supersedes the obsolete 2026-10-09 progress snapshot formerly stored here.

## Completed and reproducible technical checks

- All-articles preflight audit: **88 article files, 0 structural errors and 0 warnings** in the previously completed run after social preview fixes (PRs #74–#76). This is static markup validation, not editorial fact checking.
- Editorial release-entry schema audit: **49/49 structured release entries, 0 warnings** on main after PR #77. Three separate news cards are correctly excluded from the release-entry schema.
- PRs #78 and #79 add source checks for three recent articles and correct a narrowly unsupported phrase in Bless. Those batches do **not** cover every article.
- Latest Public Resource Audit on merge commit `570c73c4d42207dc3bde760f8ab2a722fef73a3e`: run #38942578081, completed successfully on 2026-10-16; **440 external references, 436 accessible, 0 confirmed broken, 4 indeterminate; 115 image references; 64 YouTube IDs, all 64 with accessible metadata**.
- Latest editorial audit and AdSense readiness workflow on that merge commit both completed with success. A successful readiness workflow does not mean Google has approved AdSense.

## Work that has NOT been completed

1. **Claim-by-claim factual validation across all 88 articles.** The claims inventory contains candidates to review, not 784 verified facts. Existing evidence logs document only limited batches.
2. **Copyright and reuse permission** for externally hosted images. A source URL, copyright notice or working HTTP response is not a reuse license.
3. **Real-browser playback tests** for each YouTube embed and region, including consent, CSP and user interaction.
4. Manual inspection of the **four indeterminate external URLs** in the current resource report. Indeterminate does not mean broken.
5. Live Search Console indexing, user experience/Core Web Vitals and actual AdSense approval.

## Canonical evidence

- `audits/final-inventory-metadata-2026-10-16.md` — 88-file sitemap/metadata inventory.
- `audits/all-88-articles-preflight-findings-2026-10-16.md` — initial preflight and remediation history.
- `audits/editorial-source-verification-batch1-2026-10-16.md`, `audits/editorial-media-review-batch2-2026-10-16.md`, `audits/editorial-source-media-batch3-2026-10-16.md`, `audits/editorial-source-media-batch4-2026-10-16.md`, `audits/editorial-official-sources-batch5-2026-10-16.md` — limited evidence-backed source/media reviews.
- https://github.com/redessmartonline/aninextup/actions/runs/38942578081 — latest confirmed external-resource report.

## Editorial change policy

Correct only independently demonstrated inaccuracies. Do not change site design, search position, cover artwork, trailers, article URLs, or intentionally disabled workflows to make an audit look clean. Future verification must record exact claim, dated primary source, decision and limitation.
