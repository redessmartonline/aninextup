"""Install the shared sharing/comment module on published article pages; idempotent."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
BLOCK='''<section class="article-community" aria-label="Share and discuss this article"><div class="ac-share"><h2>Share this article</h2><p class="ac-sub">Know someone waiting for this anime? Send them the guide.</p><div class="ac-buttons"></div><p class="ac-share-status" role="status"></p></div><div class="ac-discussion"><div class="ac-heading"><h2>Join the discussion</h2><span class="ac-count">Comments</span></div><p class="ac-sub">Share your thoughts with other anime fans. Display names are chosen by readers.</p><form class="ac-form" method="post" action="/api/comments"><p class="ac-reply-note" hidden></p><label for="comment-name">Display name</label><input id="comment-name" name="name" minlength="2" maxlength="60" placeholder="How should we call you?" required autocomplete="off"><label for="comment-body">Your comment</label><textarea id="comment-body" name="body" minlength="3" maxlength="2000" placeholder="Add to the conversation. Please avoid spoilers." required></textarea><div class="ac-honey" hidden aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div><div class="ac-bottom"><p>Be respectful. No spam or personal information. Comments are reviewed before appearing. <a href="/privacy">Privacy Policy</a> · <a href="/contact">Report a comment</a></p><button class="ac-submit" type="submit" disabled>POST COMMENT →</button></div><p class="ac-status" role="status" aria-live="polite">Loading comments…</p></form><div class="ac-list"></div><button class="ac-load" type="button" hidden>Load more comments</button><noscript>Sharing and comments require JavaScript.</noscript></div></section>'''
def main():
 count=0
 for path in sorted((ROOT/'articles').glob('*.html')):
  text=path.read_text()
  if 'noindex' in text.split('</head>')[0]:continue
  if 'class="article-community"' not in text:
   match=re.search(r'<section\b[^>]*(?:aria-labelledby="related-releases-heading"|class="related-releases")[^>]*>',text)
   if not match:raise ValueError('Missing related section: '+str(path))
   text=text[:match.start()]+BLOCK+text[match.start():]
  css='<link rel="stylesheet" href="/assets/article-community.css?v=20261031a">'
  js='<script defer src="/assets/article-community.js?v=20261031a"></script>'
  if '/assets/article-community.css?' not in text:text=text.replace('</head>',css+'\n</head>',1)
  if '/assets/article-community.js?' not in text:text=text.replace('</body>',js+'</body>',1) if '</body>' in text else text+js+'\n'
  if text!=path.read_text():path.write_text(text);count+=1
 print('Article community modules updated:',count)
if __name__=='__main__':main()
