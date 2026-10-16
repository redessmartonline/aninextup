# Social sharing image remediation — 2026-10-16

Baseline: full 88-article preflight found zero errors and three missing `og:image` warnings.

## Corrected in this PR
- `articles/ace-of-diamond-second-season.html`: added `og:image` and `twitter:image` pointing to the **existing** repository asset `/assets/images/covers/ace-of-diamond-second-season.jpg`. The asset path was verified in the GitHub main tree. No cover, article body, layout or trailer was modified. This does not independently certify ownership or licensing of the existing asset.

## Still pending: no safe JPG/PNG candidate established
- `articles/bass-x-machina-release-date.html`: the article includes official Netflix YouTube teaser `CWbZBIrEfqI`, corroborated by the Netflix channel and Netflix media center. Its YouTube thumbnail is a plausible share-image candidate, but use as an externally hotlinked OG asset and republication permission have not been established. The other embedded thumbnail `jjr5mf9i42Q` has not been verified as the correct share image. Do not silently substitute unrelated Netflix October imagery.
- `articles/manchuria-opium-squad-anime.html`: the repo already contains `/assets/images/manchuria-opium-squad-anime.svg`, but SVG Open Graph preview support is inconsistent. Pony Canyon published a promotional visual on 2026-10-05 (https://news.ponycanyon.co.jp/2026/10/126491), but republication permission and an appropriate stable image URL remain unconfirmed. Do not fabricate or silently copy a copyrighted JPG.

## Validation and limits
- Run `python scripts/audit_all_articles_preflight.py --root articles --out audits/generated` on this branch; expected static result is **0 errors, 2 missing-og-image warnings**. This expectation is not a claimed executed result until CI completes.
- Confirm OG image URLs in public HTML after merge and deployment. Local file presence is not a public HTTP status check.
- Do not treat missing OG imagery as an AdSense policy violation, or infer image reuse rights from the existence of an official press release.
