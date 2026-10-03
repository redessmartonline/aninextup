# aninextup
AniNextUp - Anime releases, streaming guides, calendars and news


## Content workflow
AniNextUp uses `assets/data.js` as the central release index. Add or update an anime there once with: `id`, `title`, `date` (or `null`), `dateLabel`, `platform`, `article`, `category`, `status`, and `image`. The Home, Today, This Week, Calendar, Where to Watch, and Search views read from this shared index automatically.

Release status values:
- `confirmed` — exact date confirmed.
- `month-confirmed` — month known, exact day pending.
- `tba` — date not announced.

Site timezone is configured once in `ANINEXTUP_DATA.site.timezone`.
