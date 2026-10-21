import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from editorial_dates import editorial_date_errors, article_lastmod
from sync_sitemap_dates import sync_sitemap

def page(published='2026-10-14', modified='2026-10-16', visible='2026-10-16'):
    data = {'@type': 'NewsArticle', 'datePublished': published, 'dateModified': modified}
    return '<script type="application/ld+json">'+json.dumps(data)+'</script><p class="editorial-details">Updated: <time datetime="'+visible+'">Date</time></p>'

class EditorialDatesTest(unittest.TestCase):
    def test_mismatches_block_preflight(self):
        self.assertEqual(editorial_date_errors(page(visible='2026-10-14')), ['visible_article_update_mismatch'])
        self.assertEqual(editorial_date_errors(page()), [])

    def test_modification_cannot_precede_publication(self):
        self.assertIn('article_modified_before_published', editorial_date_errors(page(modified='2026-10-13')))

    def test_video_and_release_dates_are_not_editorial_dates(self):
        text=page()+'<script type="application/ld+json">{"@type":"VideoObject","uploadDate":"2026-10-21T12:00:00Z"}</script><time datetime="2027-01-10">Premiere</time>'
        self.assertEqual(article_lastmod(text),'2026-10-16')
        self.assertEqual(editorial_date_errors(text),[])

    def test_sitemap_keeps_original_dates_and_is_idempotent(self):
        raw='<urlset><url><loc>https://aninextup.com/</loc><lastmod>2026-10-21</lastmod></url><url><loc>https://aninextup.com/articles/example</loc><lastmod>2026-10-21</lastmod></url></urlset>'
        result,changed=sync_sitemap(raw,{'example':page()})
        self.assertEqual(changed,['example'])
        self.assertIn('<loc>https://aninextup.com/</loc><lastmod>2026-10-21</lastmod>',result)
        self.assertIn('<loc>https://aninextup.com/articles/example</loc><lastmod>2026-10-16</lastmod>',result)
        self.assertEqual(sync_sitemap(result,{'example':page()}),(result,[]))

    def test_both_visible_dates_and_graph_metadata(self):
        text=page().replace('Updated:', 'Published:').replace('datetime="2026-10-16"','datetime="2026-10-14"')
        self.assertEqual(editorial_date_errors(text),[])
        self.assertEqual(article_lastmod('<script type="application/ld+json">{"@graph":[{"@type":["Article"],"datePublished":"2026-10-14"}]}</script>'),'2026-10-14')

if __name__ == '__main__':
    unittest.main()
