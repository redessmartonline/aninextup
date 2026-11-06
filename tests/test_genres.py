"""Check the generated genre directory, homepage placement and site navigation."""
import re
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
class GenreTests(unittest.TestCase):
    def test_directory_links_and_sections(self):
        source=(ROOT/'genres.html').read_text();parser=Links();parser.feed(source)
        self.assertEqual(len(re.findall(r'class="genre-section"',source)),11)
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertEqual(len(re.findall(r'<h1\b',source)),1)
        for href in parser.links:
            url=urlsplit(href)
            if url.scheme or not href.startswith(('/', '#')):continue
            path=ROOT/(url.path.lstrip('/') or 'genres.html')
            if not path.suffix:path=path.with_suffix('.html')
            self.assertTrue(path.is_file(),href)
            if url.fragment:
                target=Links();target.feed(path.read_text());self.assertIn(url.fragment,target.ids,href)
    def test_home_placement(self):
        home=(ROOT/'index.html').read_text()
        self.assertLess(home.index('class="home-news-overview"'),home.index('class="home-genres"'))
        self.assertLess(home.index('class="home-genres"'),home.index('class="home-more-news"'))
        self.assertEqual(home.count('class="genre-tile"'),6)
    def test_every_header_has_static_genres_after_watch(self):
        for path in [*ROOT.glob('*.html'),*(ROOT/'articles').glob('*.html')]:
            source=path.read_text();header=re.search(r'<header class="site-header">.*?</header>',source,re.S)
            if not header or '<nav' not in header[0]:continue
            self.assertEqual(header[0].count('href="/genres"'),1,path.name)
            self.assertRegex(header[0],r'WHERE TO WATCH</a><div class="nav-category-item" data-category-menu="genres"><a[^>]*href="/genres">GENRES</a>')
            self.assertEqual(header[0].count('data-category-menu="news"'), 1, path.name)
            primary = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([A-Z][A-Z -]+)</a>', header[0])
            self.assertEqual(primary, [
                ('/', 'HOME'), ('/today', 'TODAY'), ('/this-week', 'THIS WEEK'),
                ('/calendar', 'CALENDAR'), ('/where-to-watch', 'WHERE TO WATCH'),
                ('/genres', 'GENRES'), ('/news', 'NEWS'), ('/contact', 'CONTACT'),
            ], path.name)
            for asset in ('genres-menu', 'mobile-menu'):
                self.assertEqual(len(re.findall(rf'src="/assets/{asset}\.js\?v=', source)), 1, path.name)
if __name__=='__main__':unittest.main()
