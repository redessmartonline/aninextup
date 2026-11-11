# AdSense rejection investigation — 2026-10-16

The user's AdSense screenshot says 'No se aprobó su cuenta' and 'Cumpla las Políticas del Programa de AdSense'. It does not identify a specific violation. The user previously used the account for YouTube and reports no duplicate account.

The homepage includes AdSense account tags and matching ads.txt publisher ID. robots.txt allows crawling. Technical audits passed for 88 articles, but they do not prove editorial originality or Google approval.

Sampled articles on Berserk of Gluttony Season 2, Ghost of Tsushima: Legends and I Lost My Adventurer's License include contextual explanations and source links; these three samples cannot certify all 88 articles. The homepage uses externally hosted artwork and thumbnails, which may require separate rights clearance.

Priorities before resubmission: manually review original value and factual sourcing across all articles; verify rights to externally hosted images; confirm editorial transparency matches actual process; inspect account-level requirements. No specific policy violation has been established. No public pages, covers, trailers, search layout or ads settings changed.


## Executed all-article screening — 2026-10-16

The repository now includes `scripts/audit_adsense_originality_and_rights.py` and the dedicated `adsense-editorial-evidence-review.yml` workflow. GitHub Actions run [38948444827](https://github.com/redessmartonline/aninextup/actions/runs/38948444827) completed **successfully**, producing the downloadable `adsense-editorial-evidence` artifact (ID `12067128043`, 11,249 bytes) with four CSVs: article lengths, exact repeated paragraphs, overlapping seven-word sequences, and image-by-image rights evidence. This confirms the screening completed, **not** that there are zero editorial risks.

### Rights decision

The image report defaults every image to `UNVERIFIED`. Public accessibility, official source attribution, image captions and YouTube thumbnails are not proof of permission to republish. **No external image has been marked cleared without a license or other applicable rights basis.** Actual rights resolution requires a rights-holder license, qualifying press-use terms, or a replacement with confirmed lawful provenance. The site's covers were preserved pending that evidence; this is an unresolved clearance task, not a completed legal audit.

### Editorial decision

The generated CSVs identify candidates for manual review; numerical overlap alone does not establish plagiarism, and a short article alone does not prove low value. Any corrective edits should cite the exact paragraph and supporting source before changing published HTML. The artifact needs manual examination to determine which specific pages require edits.
