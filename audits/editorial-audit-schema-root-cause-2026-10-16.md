# Editorial audit schema investigation — 2026-10-16

The latest main editorial audit workflow completed successfully but reported 7 warnings in 52 rows: `invalid_status: 3`, `missing_field: 3`, `invalid_date: 1`.

## Root cause established from source
`scripts/editorial_audit.py` scanned **every line containing `{id:"`** in `assets/data.js` as though it were a release calendar entry. The data file contains different schemas:
- `anime[]` includes **49 structured release entries** with `status`, `date`, `platform`, etc.
- `anime[]` also includes **3 news teaser cards** with `tag` and `description` instead of release fields: Bless Anime Akiharu Nakano; I Got a Cheat Skill Season 2; In a World Full of Zombies. They caused the three `invalid_status` and three `missing_field` warnings.
- `anime[]` also included the Yumeneko Connect article entry with `date:"TBA"` and `status:"confirmed"`. This was a genuine metadata inconsistency: no exact release date has been announced. The article's embedded index and central data entry were both corrected to `date:null`, `dateLabel:"TBA"`, `status:"tba"`.

## Patch
The release validator now selects `anime[]` entries containing a `status` property. It counts but excludes the three differently structured news cards and all `guides[]` cards from release-specific validation. The Yumeneko release-status metadata was also corrected consistently in `assets/data.js` and its embedded article index. No visible article body, image, trailer, or design was modified.

**Expected** after CI: 49 structured entries, 3 excluded news cards, 0 warnings. This is not evidence that every claim or news card has been fact checked. Future work should implement separate schema checks for the editorial news cards.

## Media checks on latest main
Public-resource audit run https://github.com/redessmartonline/aninextup/actions/runs/38927261126 reported 440 external references, 436 accessible, 0 confirmed broken, 4 indeterminate; 64 YouTube IDs had accessible metadata, but actual player embed playback was not tested.

## Official source spot-check
- Netflix's Anime NYC announcement confirms Bass X Machina November 3, 2026 global release and teaser: https://about.netflix.com/ja/news/anime-nyc-2026.
- Pony Canyon's October 5 release confirms Manchuria Opium Squad anime adaptation and announcement visual; production staff and studio were not yet announced: https://news.ponycanyon.co.jp/2026/10/126491.

These two official checks are a **spot-check**, not a comprehensive factual review of 88 articles.
