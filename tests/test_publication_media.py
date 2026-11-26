import copy
import json
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_publication_media import media_errors
from validate_video_schema import trailer_markup_errors
import prepare_public_media


class PublicationMediaTests(unittest.TestCase):
    def setUp(self):
        slug = 'the-dangers-in-my-heart-season-3'
        self.article = (ROOT / 'articles' / f'{slug}.html').read_text()
        self.review = json.loads((ROOT / 'editorial/reviews' / f'{slug}.json').read_text())

    def test_publication_with_reviewed_cover_and_video(self):
        self.assertEqual(media_errors(self.article, self.review), [])

    def test_svg_cannot_be_declared_official_cover(self):
        record = copy.deepcopy(self.review)
        record['cover']['path'] = '/assets/images/bokuyaba-season-3-release-guide.svg'
        self.assertTrue(any('Official cover' in error for error in media_errors(self.article, record)))

    def test_video_link_alone_cannot_replace_player(self):
        link_only = self.article.replace('class="lite-trailer"', 'class="removed-player"')
        self.assertTrue(trailer_markup_errors(link_only))
        self.assertTrue(media_errors(link_only, self.review))

    def test_trailer_cannot_be_silently_left_unreviewed(self):
        self.review.pop('video')
        self.assertIn('Missing official trailer availability review', media_errors(self.article, self.review))


class PublicMediaBuildTests(unittest.TestCase):
    def test_retires_image_downloads_and_stale_credits_but_keeps_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / 'guide.html'
            page.write_text('<p class="image-credit">Official key visual</p>'
                '<p><a href="https://example.org/visual.jpg?size=large">Visual</a></p>'
                '<a href="https://example.org/news">Announcement</a>'
                '<a href="https://example.org/press.pdf">Press release</a>'
                '<a href="https://www.youtube.com/watch?v=12345678901">Trailer</a>')
            prepare_public_media.prepare(page)
            cleaned = page.read_text()
            self.assertNotIn('image-credit', cleaned)
            self.assertNotIn('visual.jpg', cleaned)
            self.assertIn('https://example.org/news', cleaned)
            self.assertIn('https://example.org/press.pdf', cleaned)
            self.assertIn('https://www.youtube.com/watch?v=', cleaned)
            prepare_public_media.prepare(page)
            self.assertEqual(page.read_text(), cleaned)

    def test_audit_reports_remote_artwork_and_direct_movie_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / 'guide.html'
            page.write_text('<img src="https://example.org/key-visual.jpg">'
                            '<a href="https://example.org/episode.mp4">Episode</a>')
            with patch.object(prepare_public_media, 'ROOT', root):
                findings = prepare_public_media.public_media_audit([page])
            self.assertEqual(len(findings), 2)


if __name__ == '__main__':
    unittest.main()
