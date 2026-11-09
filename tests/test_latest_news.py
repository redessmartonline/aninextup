import tempfile
import json
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import build_latest_news

class ArticleMetadataTests(unittest.TestCase):
    def extract_fixture(self, source):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"new-story.html"
            path.write_text(source)
            return build_latest_news.extract(path)

    def test_standard_article_without_internal_index_is_included(self):
        row=self.extract_fixture('<meta property="og:title" content="New story"><meta name="description" content="Verified announcement"><meta property="og:image" content="/cover.jpg"><script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-11-04"}</script>')
        self.assertEqual(row["title"],"New story")
        self.assertEqual(row["published"],"2026-11-04")
        self.assertEqual(row["article"],"articles/new-story")

    def test_non_article_page_is_excluded(self):
        self.assertIsNone(self.extract_fixture('<meta property="og:title" content="Utility page">'))

    def test_noindex_article_is_excluded(self):
        self.assertIsNone(self.extract_fixture('<meta name="robots" content="noindex,follow"><meta property="og:title" content="Draft"><script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-11-04"}</script>'))

class UpdatedGuideTests(unittest.TestCase):
    def test_only_editorial_updates_to_release_guides_qualify(self):
        page = (
            '<meta property="og:title" content="Anime Viewing Guide">'
            '<script type="application/ld+json">{"@type":"VideoObject",'
            '"dateModified":"2026-11-10"}</script>'
            '<script type="application/ld+json">{"@type":"NewsArticle",'
            '"datePublished":"2026-11-08","dateModified":"EDITORIAL_DATE"}</script>'
        )
        item = {"title": "Anime"}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "guide.html"
            path.write_text(page.replace("EDITORIAL_DATE", "2026-11-09"))
            self.assertIsNone(build_latest_news.updated_guide(path, item))
            summary = '<section class="release-summary"></section>'
            path.write_text(summary + page.replace("EDITORIAL_DATE", "2026-11-08"))
            self.assertIsNone(build_latest_news.updated_guide(path, item))
            path.write_text(summary + page.replace("EDITORIAL_DATE", "2026-11-09"))
            guide = build_latest_news.updated_guide(path, item)
            self.assertEqual(guide["updated"], "2026-11-09")
            self.assertEqual(guide["title"], "Anime Viewing Guide")

class LatestNewsArchiveTests(unittest.TestCase):
    def test_every_published_story_remains_discoverable(self):
        expected={row["article"] for path in build_latest_news.ARTICLES.glob("*.html") if (row:=build_latest_news.extract(path))}
        rows=json.loads(build_latest_news.OUT.read_text())["items"]
        urls=[row["article"] for row in rows]
        self.assertEqual(set(urls),expected)
        self.assertEqual(len(urls),len(set(urls)))
        source=(build_latest_news.ROOT/"index.html").read_text()
        for url in expected:
            self.assertIn('href="/'+url+'"',source)

if __name__=="__main__":unittest.main()
