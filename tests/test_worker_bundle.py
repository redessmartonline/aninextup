"""Prevent raw Cloudflare Builds from replacing the prepared production assets."""
from pathlib import Path
import importlib.util
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('worker_bundle', ROOT / 'scripts/check_worker_bundle.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkerBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'articles').mkdir()
        self.page = self.root / 'articles/guide.html'
        self.cover = self.root / 'assets/article-covers/guide.png'
        self.cover.parent.mkdir(parents=True)
        self.cover.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\0\0\0\rIHDR' + struct.pack('>II', 1200, 630))
        self.page.write_text('<img class="article-original-cover" src="/assets/article-covers/guide.png">'
            '<meta property="og:image" content="https://aninextup.com/assets/article-covers/guide.png">'
            '<meta name="twitter:image" content="https://aninextup.com/assets/article-covers/guide.png">')

    def test_complete_bundle_passes(self):
        self.assertEqual(module.bundle_errors(self.root), [])

    def test_raw_source_fails(self):
        self.page.write_text('<figure><img src="/assets/images/guide.webp"></figure>')
        self.assertTrue(module.bundle_errors(self.root))

    def test_missing_cover_fails(self):
        self.cover.unlink()
        self.assertTrue(module.bundle_errors(self.root))

    def test_html_fallback_instead_of_png_fails(self):
        self.cover.write_text('<html>404</html>')
        self.assertTrue(module.bundle_errors(self.root))

    def test_wrong_dimensions_fail(self):
        self.cover.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\0\0\0\rIHDR' + struct.pack('>II', 600, 315))
        self.assertTrue(module.bundle_errors(self.root))

    def test_mismatched_sharing_image_fails(self):
        self.page.write_text(self.page.read_text().replace('property="og:image"', 'property="old:image"'))
        self.assertTrue(module.bundle_errors(self.root))

    def test_second_unprepared_article_blocks_whole_bundle(self):
        (self.root / 'articles/second.html').write_text('<article>New article</article>')
        self.assertTrue(module.bundle_errors(self.root))


if __name__ == '__main__':
    unittest.main()
