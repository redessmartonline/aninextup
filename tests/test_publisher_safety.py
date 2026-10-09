import importlib.util
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('publisher',ROOT/'scripts'/'auto_publish_news.py')
publisher=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)

class PublisherSafety(unittest.TestCase):
    def test_feed_media(self):
        import xml.etree.ElementTree as ET
        node=ET.fromstring('<item xmlns:media="http://search.yahoo.com/mrss/"><media:thumbnail url="https://img1.ak.crunchyroll.com/cover.jpg" /></item>')
        self.assertEqual(publisher.feed_image(node),'https://img1.ak.crunchyroll.com/cover.jpg')
    def test_reject_untrusted_image(self):
        import xml.etree.ElementTree as ET
        node=ET.fromstring('<item><enclosure url="https://evil.example/cover.jpg" type="image/jpeg"/></item>')
        self.assertEqual(publisher.feed_image(node),'')
        self.assertIsNone(publisher.verified_image_bytes('https://evil.example/cover.jpg'))
    def test_editorial_short_rejected(self):
        self.assertIsNone(publisher.editorial_sections('Anime','Short description.','https://crunchyroll.com/news'))
    def test_editorial_complete_accepted(self):
        desc=' '.join(f'The official announcement provides verified detail number {i} about the upcoming anime release and the publisher confirms this information.' for i in range(10))
        self.assertIn('What the official source reports',publisher.editorial_sections('Anime',desc,'https://crunchyroll.com/news'))
    def test_image_not_erased_before_save(self):
        code=(ROOT/'scripts'/'auto_publish_news.py').read_text()
        self.assertIn('and not image_payload:',code)
        self.assertIn('if image_payload:',code)
        self.assertIn('if dry_run:',code)

if __name__=='__main__':unittest.main()
