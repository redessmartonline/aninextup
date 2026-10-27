import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_video_schema import video_schema_errors
spec = importlib.util.spec_from_file_location('publisher', ROOT / 'scripts/auto_publish_news.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

class OfficialTrailerTests(unittest.TestCase):
    def test_detects_source_video_without_trailer_in_headline(self):
        for link in ('https://www.youtube.com/embed/Ak8DnZUIPSk',
                     'https://www.youtube-nocookie.com/embed/Ak8DnZUIPSk',
                     'https://www.youtube.com/watch?v=Ak8DnZUIPSk',
                     'https://youtu.be/Ak8DnZUIPSk'):
            with self.subTest(link=link):
                response = MagicMock()
                response.__enter__.return_value = response
                response.geturl.return_value = 'https://www.crunchyroll.com/news/announcement'
                response.headers = {'Content-Type': 'text/html'}
                response.read.return_value = ('<iframe src="'+link+'"></iframe>').encode()
                with patch.object(publisher.urllib.request, 'urlopen', return_value=response):
                    result = publisher.official_trailer_embed(response.geturl(), 'January Premiere', '/assets/verified.webp')
                self.assertIn('data-youtube="Ak8DnZUIPSk"', result)
                self.assertIn('<button', result)
                self.assertIn('src="/assets/verified.webp"', result)
                self.assertNotIn('data-external-only', result)

    def test_does_not_guess_video_when_source_has_none(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = 'https://www.crunchyroll.com/news/announcement'
        response.headers = {'Content-Type': 'text/html'}
        response.read.return_value = b'<p>Release confirmed; no video announced.</p>'
        with patch.object(publisher.urllib.request, 'urlopen', return_value=response):
            self.assertEqual(publisher.official_trailer_embed(response.geturl(), 'Premiere'), '')

    def test_registered_available_video_cannot_be_silently_omitted(self):
        path = ROOT / 'articles/mashle-season-3-release-date.html'
        source = path.read_text()
        self.assertEqual(video_schema_errors(source), [])
        self.assertTrue(video_schema_errors(source.replace('data-youtube="Ak8DnZUIPSk"', 'data-youtube="wrong-id"')))
        self.assertTrue(video_schema_errors(source.replace('data-youtube="Ak8DnZUIPSk"', 'data-external-only="true" data-youtube="Ak8DnZUIPSk"')))
        self.assertTrue(video_schema_errors(source.replace('class="trailer-play"', 'class="missing-button"')))

    def test_verified_player_does_not_require_fabricated_schema_date(self):
        for slug in ('mashle-season-3-release-date', 'akane-banashi-season-2-release-date', 'medalist-movie-release-date'):
            source = (ROOT / 'articles' / (slug+'.html')).read_text()
            self.assertNotIn('"@type":"VideoObject"', source)
            self.assertEqual(video_schema_errors(source), [])

if __name__ == '__main__': unittest.main()
