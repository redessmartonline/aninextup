# AniNextUp article comments

Public comments are served at `/api/comments`; submissions start as `pending`. No public moderation endpoint or moderator token exists. Only `approved` records are returned, in pages of 20. Names are reader-chosen, not verified identities. Comments never subscribe a visitor to the newsletter.

To review: Cloudflare dashboard → Storage & databases → D1 → `aninextup-newsletter` → `article_comments`. Filter `state = pending` and review `article`, `display_name`, `body`, `parent_id` and `id`. Do not put pending text into public GitHub issues or workflow logs.

To moderate: GitHub Actions → **Moderate article comment** → Run workflow on main → enter the numeric `comment_id` and choose `approved`, `rejected` or `pending`. `approved` publishes immediately; either other state hides it. This uses existing repository-authorized Cloudflare credentials without exposing them. Check the article's public comments after the action completes. Readers can request removal or report an issue through Contact.

Limits: 3 submissions/IP/hour and 100 submissions globally/hour, honeypot, 10 KB body cap, 2–60 character names, 3–2,000 character text, duplicate suppression. IP-derived rate hashes expire on later submissions after 24 hours. Pending content is not emailed or auto-approved. Rate limits supplement manual moderation and are not a substitute for a full abuse detection service.

`build_article_community.py` runs on every production deployment so future published article pages receive the module too. Related releases, newsletter and canonical URLs are preserved. The live integration check submits a unique unpublished test comment, verifies storage/pending privacy, and removes only that record. Approval, rejection, pagination and reply scope are tested using an in-memory database.
