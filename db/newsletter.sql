CREATE TABLE IF NOT EXISTS newsletter_subscribers (
 email TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('pending','active','unsubscribed')),
 confirm_hash TEXT UNIQUE, confirm_expires INTEGER, unsubscribe_token TEXT NOT NULL UNIQUE,
 created_at INTEGER NOT NULL, confirmed_at INTEGER, cursor TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS newsletter_active ON newsletter_subscribers(state,cursor);
CREATE TABLE IF NOT EXISTS newsletter_limits(key TEXT NOT NULL,period INTEGER NOT NULL,count INTEGER NOT NULL,PRIMARY KEY(key,period));
