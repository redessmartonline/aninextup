# Published cover inputs

Each published article has a manifest entry here and a matching entry in
`editorial/cover-provenance.json`. Production uses these original editorial
illustrations. Archived source-article heroes and thumbnails are not the public
cover set and are excluded by the preparation step and `.assetsignore`.

When adding or replacing artwork:

1. Create an original editorial illustration. Do not copy a promotional still,
   character sheet, logo, watermark or another artist's composition. Do not label
   the result an official visual. Generated output still needs visual review.
2. Save the selected project asset and its manifest entry. Record the exact
   source raster SHA-256 (decoded bytes for inline base64), sourceFile, manifest,
   and panel coordinates or null in the provenance entry.
3. Record origin `project-editorial-artwork`, visualReviewOn, and the actual
   review notes. Preserve a real provenanceCommit when the source is already
   committed; for newly generated art, use a generationRecord object containing
   tool `image_gen`, the actual prompt, and generatedOn. Do not invent a license,
   generation history, or verification date. No second commit is needed merely
   to know the new commit's SHA.
4. Verify that the illustration is suitable for the subject without suggesting
   that its setting, character appearance or objects are confirmed production
   material. Identity hashes and project history are not legal clearance.
5. Run the cover tests, source validation and the normal prepared-build media
   checks. Keep the established public cover URLs and responsive variants.

An unregistered input or changed raster fails the production build before any
cover is replaced. The provenance registry is repository-only, not a public
license certificate.
