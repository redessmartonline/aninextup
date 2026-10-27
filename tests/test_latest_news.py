import json
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import build_latest_news

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
