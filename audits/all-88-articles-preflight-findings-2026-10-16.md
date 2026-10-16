# Full 88-article preflight — execution findings (2026-10-16)

Source: GitHub Actions run https://github.com/redessmartonline/aninextup/actions/runs/38923816720 on PR #74.

- 88 article HTML files scanned.
- 0 errors; 3 warnings, all `missing_og_image`.
- GitHub job completed successfully and uploaded the full per-article JSON and Markdown reports as artifact `all-articles-preflight` (artifact ID 12056165925).
- These are static metadata checks, **not** factual verification of all 784 candidate claims, image licensing, or real browser playback.

## Confirmed warning locations

| Article | Finding | Existing visual evidence | Safe next step |
|---|---|---|---|
| `articles/ace-of-diamond-second-season.html` | No `og:image` | No article `img` or JSON-LD image found | Choose a verified, rights-cleared cover; do not invent an image URL |
| `articles/bass-x-machina-release-date.html` | No `og:image` | Page already uses YouTube thumbnail URLs `jjr5mf9i42Q` and `CWbZBIrEfqI` | Confirm which is the official trailer and sharing-image permissions before selecting an OG image |
| `articles/manchuria-opium-squad-anime.html` | No `og:image` | No article `img` or JSON-LD image found | Choose a verified, rights-cleared cover; do not invent an image URL |

## Disposition

No published article has been changed by this PR. The three warnings are legitimate social-sharing metadata omissions but **not fatal errors**. Two articles do not currently contain an image URL suitable for safe automatic reuse, and the third has multiple video thumbnails without confirmed reuse rights. Automatically assigning a random cover could introduce factual or rights problems. Leave the existing article presentation unchanged until suitable image assets are verified.

## Reproduction

`python scripts/audit_all_articles_preflight.py --root articles --out audits/generated`

The generated reports include each of the 88 filenames and their individual findings. The workflow is read-only and uploads both reports for inspection.
