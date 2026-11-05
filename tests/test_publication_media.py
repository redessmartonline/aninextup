import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_publication_media import media_errors
from validate_video_schema import trailer_markup_errors


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


if __name__ == '__main__':
    unittest.main()
