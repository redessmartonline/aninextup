CREATE TABLE IF NOT EXISTS article_comments (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 article TEXT NOT NULL, display_name TEXT NOT NULL, body TEXT NOT NULL,
 parent_id INTEGER REFERENCES article_comments(id),
 state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','approved','rejected')),
 created_at TEXT NOT NULL, moderated_at TEXT, fingerprint TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS comments_public ON article_comments(article,state,id);
CREATE TABLE IF NOT EXISTS comment_limits (key TEXT NOT NULL, period INTEGER NOT NULL, count INTEGER NOT NULL, PRIMARY KEY(key,period));
