# AniNextUp comments

Clean comments publish immediately. Local heuristic rules retain comments with URLs, email addresses, HTML, common promotional phrases or extreme character repetition as pending. These rules reduce spam but do not guarantee detection. Rate limits and the honeypot remain enabled. Existing pending comments are unchanged.

Review in Cloudflare D1 → aninextup-newsletter → article_comments. Use the Moderate article comment GitHub workflow with the numeric ID and approved/rejected/pending.

Check pending article comments runs hourly and logs only the pending count and latest pending ID, never comment text or names. ChatGPT checks these results hourly and alerts on new pending comments. No public moderation endpoint is added.
