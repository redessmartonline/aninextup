import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("news_categories",ROOT/"scripts"/"news_categories.py")
module=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class NewsCategoryTests(unittest.TestCase):
    def classify(self,title,description="A new anime announcement from its official production team."):
        return module.classify_news_category({"title":title,"description":description,"article":description})

    def test_first_adaptation_is_new_anime(self):
        self.assertEqual(self.classify("The Boxer Anime Announced"),"new-anime")

    def test_sequel_trailer_stays_returning_series(self):
        self.assertEqual(self.classify("One-Punch Man Season 3 Part 2 Reveals a New Trailer"),"returning-series")

    def test_standalone_trailer_news(self):
        self.assertEqual(self.classify("BLEACH: The Last PV Is Now Available","The anime trailer is now available."),"trailers-cast")

    def test_release_update(self):
        self.assertEqual(self.classify("Anime Film Sets Its Release Date","The anime film opens in Japanese theaters on October 23."),"release-news")

    def test_game_code_guide_is_not_news(self):
        page=(ROOT/"articles"/"anime-mysterious-codes-october-2026.html").read_text(encoding="utf-8")
        self.assertIsNone(module.classify_news_category(page))

    def test_unmatched_story_is_not_forced(self):
        self.assertIsNone(module.classify_news_category({"title":"Anime Mysterious Codes","description":"Roblox game codes"}))


    def test_dropdown_routes_to_real_category_filters(self):
        menu=(ROOT/"assets"/"mobile-menu.js").read_text(encoding="utf-8")
        app=(ROOT/"assets"/"app.js").read_text(encoding="utf-8")
        news=(ROOT/"news.html").read_text(encoding="utf-8")
        self.assertIn("link.href='/news?category='+key+'#category-'+key",menu)
        self.assertIn("location.hash.match(/^#category-",app)
        for key in ("new-anime","returning-series","trailers-cast","release-news"):
            self.assertIn(f'id="category-{key}"',news)

    def test_existing_category_backfill_is_reviewed(self):
        data=(ROOT/"assets"/"data.js").read_text(encoding="utf-8")
        self.assertNotIn('article:"articles/anime-mysterious-codes-october-2026",newsCategory:',data)
        self.assertIn('article:"articles/the-one-piece-netflix-february-2027",newsCategory:"new-anime"',data)
        self.assertIn('article:"articles/sakamoto-days-season-2",newsCategory:"returning-series"',data)
        self.assertIn('article:"articles/fall-2026-anime-calendar",newsCategory:"release-news"',data)

if __name__=="__main__": unittest.main()
