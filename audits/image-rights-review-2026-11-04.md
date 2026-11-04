# AniNextUp image provenance and reuse-rights review — November 4, 2026

## Result

The article-image inventory contains **208 distinct normalized image references** across 132 articles. The previous 227 count treated some relative and absolute references to the same file separately. This inventory covers HTML img/src and img/data-src only; it does not certify every CSS image, social image, logo or non-article page.

**No asset-specific reproduction license was established in this review. No asset is marked DOCUMENTED_PERMISSION.** Published source attribution and copyright identification are separate from permission. This is not a finding that every image is unlawful, and no blanket fair-use determination has been made.

## Provenance recovered and retained

- Recovered 231 source/local mappings from all 39 historical versions of assets/images/external/sources.json. Added 12 mappings recovered from earlier cover-download commits and their editorial source notes: **243 historical mappings** in the restored manifest.
- The current article inventory has **151 distinct assets with historical download/source provenance**. A historical URL identifies the documented supplier; it does not prove a license, identify every underlying rights holder, or guarantee the URL is still available.
- Fixed scripts/mirror_site_images.py so an empty run no longer overwrites the source history with an empty list. It preserves recorded evidence_commit fields and stores the latest run's count separately.
- Added 15 source credits where traceable and missing, and made one existing credit machine-readable, while retaining existing caption text and copyright notices. CDN suppliers are identified only as source hosts, not automatically as rights holders. YouTube thumbnails are linked to their original video without asserting an independent image-reproduction license.
- Kept article publication dates, modification dates, images, SEO metadata, consent gates and trailers unchanged by this attribution work.

## Records

- assets/images/external/sources.json: cumulative supplier/download history, including historical commit evidence.
- audits/generated/media-rights-register.json: distinct assets, article usages, original URL evidence, published credits and independent permission status.
- audits/generated/media-rights-register.csv: reviewable version of the same inventory.
- audits/media-permissions.json: manually recorded rights decisions. Two verified published copyright credits are documented here; both remain UNVERIFIED for reuse permission.

Rebuild the register with `python scripts/build_image_rights_register.py`. Regeneration reads the manual decision file and does not erase reviewed evidence. A DOCUMENTED_PERMISSION decision requires a named holder, evidence and a defined scope; the script does not manufacture that decision from a source URL or credit.

## Primary policy and copyright checks

Checked on 2026-11-04:

| Source | What the source establishes | What remains unestablished for these assets |
| --- | --- | --- |
| https://www.fujitv.co.jp/fujitv/news/20251389.html | The DARK MACHINE announcement publishes the visual and the Project Carbuncle / DARK MACHINE Committee copyright credit. | An asset-specific license for AniNextUp's reproduction. |
| https://toaru-project.com/item/ | The production site publishes key visuals and the Kamachi / KADOKAWA / PROJECT-ITEM credit. | An asset-specific license for AniNextUp's reproduction. |
| https://pokemon.gamespress.com/Media-Usage-Guidelines | Its limited press-content license has non-commercial and modification restrictions. | Whether a specific current AniNextUp image came from the covered press materials, and authorization for the intended monetized use. Do not apply this policy as a blanket commercial grant. |
| https://media.netflix.com/en/apply and https://media.netflix.com/en/contact-us | Approved press accounts can access publicity materials; approval is not automatic. | AniNextUp's approved access, the relevant asset terms and title-specific rights. |
| https://www.youtube.com/static?template=terms | The terms distinguish permitted embedded-player use from other reproduction and reserve underlying rights. | Permission to reuse a downloaded thumbnail independently as a site cover. Official upload provenance is not a standalone image license. |

The Netflix brand terms page required JavaScript in the retrieved source and Crunchyroll's English terms page yielded no readable text; neither was treated as evidence granting image rights. The Apothecary Diaries movie site returned 403 to this retrieval; the existing historical image-source record was retained without claiming a newly verified permission.

A narrowly scoped search of connected mail for AniNextUp-related permission/licensing/publicity subjects did not locate an image-use authorization. This is not proof that no private agreement exists. No email contents or personal correspondence have been copied into this public report; no permission requests were sent.

## Validation

Three regression tests pass for empty-run history retention, preservation of supplier attribution links during mirroring, and independent permission evidence across rebuilds. JSON-LD parses across all 132 articles. The 16 article changes were compared with their original HTML: only added credits and the classification of one existing credit changed; image tags and editorial text remain intact. The AdSense workflow now rebuilds and uploads the register; the mirror workflow runs the evidence-preservation tests.

## Remaining evidence required

For each third-party asset to be cleared, obtain or identify a license, written permission, applicable press-use terms covering the exact asset and planned use, or another properly reviewed basis. Record the evidence, permitted publication, monetization, transformations, territory, duration and required credit. Do not silently replace an UNVERIFIED status with a legal conclusion.

The imported fall-calendar and Netflix-monthly cover images still lack an established original supplier in this review. Do not invent an attribution for these files. Other older cover assets have partial provenance only; use the register for the exact per-asset record.

If the owner supplies existing permissions, record their scope and evidence references without publishing private agreements or contact details to GitHub. Keep private documents private. If authorization cannot be established, prepare a documented replacement or removal for editorial review; this task has not removed images indiscriminately or purchased any licenses.
