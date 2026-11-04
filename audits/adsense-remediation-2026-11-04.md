# AniNextUp — AdSense remediation, November 4, 2026

## Completed

- Reviewed the current HTML inventory: 132 articles. Previous technical audit run 41895192514 checked 147 HTML pages with zero errors and zero editorial/manual warnings; this does not certify editorial accuracy, copyright, consent or AdSense approval.
- Removed 286 automatically inserted inline recommendations from 108 articles. They were selected by shared title words rather than a demonstrated relationship to the paragraph. Existing manually authored links and Related releases cards are retained. The generator now only removes its legacy marked spans, so its workflow cannot reintroduce them.
- Removed the obsolete November 5 at 22:00 Watchanimee claim from Demons' Crest. Retained the user-requested guide link, clearly identified it as third-party information, and retained the separately attributed official Japanese release notice. No Dominican Republic time zone was inferred. Article modification date updated for this substantive correction; unrelated articles retain their dates.
- Generated review queues for 516 image references (227 distinct image URLs) and 92 video/article references across 132 articles. These inventories do not grant reuse permission, establish infringement, or prove video playback.

## Outstanding: certified consent management

The site uses TermsFeed Free Cookie Consent 4.2.0 with strictly-necessary defaults, tracking-gated Analytics and targeting-gated AdSense. TermsFeed explicitly states that this free product does not write a TCF string and is not Google-certified. It must not be represented as a certified CMP.

Attempting to access AdSense returned an HTTP 400 sign-in error. No account settings or messages were changed. Preserve the existing blocking behavior until a replacement is configured and tested.

When account access is available:

1. Open AdSense > Privacy & messaging > European regulations. Select aninextup.com and its privacy URL https://aninextup.com/privacy.
2. Create and publish the Google CMP message with English language support and first-layer consent, do-not-consent and preference controls. Check the account's consent-mode settings for Analytics and advertising.
3. Implement the account-provided CMP integration, then replace the TermsFeed banner and transfer script blocking to the documented CMP/TCF method. Do not leave two independent banners or make the CMP bootstrap depend on accepting the old banner.
4. Verify first visit, rejection, acceptance, preference reopening and withdrawal from applicable regions. Verify actual requests and TCF signals; a visible banner is insufficient. Keep optional tags blocked when signals are absent or invalid.
5. Update the privacy policy to describe the actual deployed provider and behavior only after the migration is live.

Official implementation references:
- https://support.google.com/adsense/answer/10960768?hl=en
- https://support.google.com/adsense/answer/13554116?hl=en
- https://support.google.com/adsense/answer/16053245?hl=en
- https://www.termsfeed.com/docs/cookie-consent/compliance/google-adsense-iab-tcf/

## Outstanding: media rights evidence

The generated image queue records references for review, not a finding of illegality. Official provenance, attribution, local hosting and HTTP availability do not independently establish permission to reuse artwork. For each distinct asset, record the rights holder, source, permitted use and evidence of a license, press-use terms, permission or another reviewed basis for use. Do not mark an asset cleared solely because it is official or credited. Replace assets whose permissible use cannot be established with material whose use is documented.

No permission documents were supplied or verified in this remediation. No rights holders were contacted. Existing assets have not been indiscriminately replaced. The code guide explicitly labels its codes as third-party reports not redeemed in-game; direct redemption remains untested.

The queues are a snapshot and must be regenerated/reconciled when new articles or assets are added. Their unverified fields are intentional; no completed review or license has been fabricated.

## Submission status

Technical/editorial cleanup is implemented. Certified CMP migration and media-rights evidence remain unresolved. Do not describe the site as fully cleared or guaranteed for AdSense on this basis.

## Verification

- Cleanup is idempotent across 132 articles; JSON-LD parses successfully. Article edits were compared against their original source, preserving consent-gated scripts and removing only generated spans except for the documented Demons' Crest correction.
- Remediation commit 079eb6b87a88b7dfd5553d8ab1ef0437f6acb9da deployed successfully in run 41902492820. AdSense readiness, indexability and all-articles preflight audits passed. The live Demons' Crest page displays the corrected third-party attribution.
- Discovery refresh exposed a stale test expecting the former calendar markup and treating site-root article links as filesystem-root paths. The test now invokes the existing expanded-calendar suite and resolves site-root links correctly. Both calendar and discovery/navigation tests pass locally after the workflow's normal prerender/navigation steps. The refresh workflow now watches these test files.
