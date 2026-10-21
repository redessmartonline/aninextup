import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_video_schema import video_schema_errors


def markup(data):
    return '<script id="schema" type="application/ld+json">' + json.dumps(data) + '</script>'


class VideoSchemaTests(unittest.TestCase):
    def test_article_date_cannot_replace_missing_video_date(self):
        data = {'@type': 'NewsArticle', 'datePublished': '2026-10-21',
                'video': {'@type': 'VideoObject', 'name': 'Trailer'}}
        self.assertEqual(len(video_schema_errors(markup(data))), 1)

    def test_nested_graph_and_type_array(self):
        data = {'@graph': [{'@type': ['VideoObject', 'CreativeWork'], 'uploadDate': '2026-10-03T12:30:00-07:00'}]}
        self.assertEqual(video_schema_errors(markup(data)), [])
        del data['@graph'][0]['uploadDate']
        self.assertEqual(len(video_schema_errors(markup(data))), 1)

    def test_invalid_dates(self):
        for value in ('', None, 20261021, '2026-02-30', 'October 21, 2026', '2026-10-21T27:00:00Z'):
            with self.subTest(value=value):
                self.assertTrue(video_schema_errors(markup({'@type': 'VideoObject', 'uploadDate': value})))

    def test_valid_dates_and_non_video_articles(self):
        for value in ('2026-10-03', '2026-10-03T12:30:00Z', '2026-10-03T12:30:00+09:00'):
            self.assertEqual(video_schema_errors(markup({'@type': 'VideoObject', 'uploadDate': value})), [])
        self.assertEqual(video_schema_errors(markup({'@type': 'NewsArticle'})), [])

    def test_invalid_json_fails_closed(self):
        self.assertTrue(video_schema_errors('<script type="application/ld+json">{broken}</script>'))


if __name__ == '__main__':
    unittest.main()
