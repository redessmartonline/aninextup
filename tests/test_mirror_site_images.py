import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from scripts import mirror_site_images as mirror


class MirrorImageTests(unittest.TestCase):
    def test_collects_rendered_image_sources_only(self):
        page = '''
        <meta property="og:image" content="https://cdn.example/og.jpg?a=1&amp;b=2">
        <img src="https://cdn.example/cover.jpg" srcset="https://cdn.example/small.jpg 1x, https://cdn.example/large.jpg 2x">
        <video poster="https://cdn.example/poster.jpg"></video>
        <link rel="preload" as="image" href="https://cdn.example/preload.jpg">
        <script>const anime = {image:"https://cdn.example/data.jpg", thumbnailUrl:"https://cdn.example/thumb.jpg"};</script>
        <style>.hero{background-image:url(https://cdn.example/background.jpg)}</style>
        <script src="https://cdn.example/app.js"></script>
        <a href="https://cdn.example/source.jpg">source</a>
        '''
        refs = mirror.image_references(page)
        self.assertIn("https://cdn.example/og.jpg?a=1&b=2", refs)
        self.assertIn("https://cdn.example/cover.jpg", refs)
        self.assertIn("https://cdn.example/large.jpg", refs)
        self.assertIn("https://cdn.example/poster.jpg", refs)
        self.assertIn("https://cdn.example/data.jpg", refs)
        self.assertIn("https://cdn.example/background.jpg", refs)
        self.assertNotIn("https://cdn.example/app.js", refs)
        self.assertNotIn("https://cdn.example/source.jpg", refs)

    def test_download_verifies_and_optimizes_raster(self):
        image = Image.new("RGB", (8, 8), color="red")
        raw = io.BytesIO()
        image.save(raw, format="PNG")

        class Response(io.BytesIO):
            headers = {"Content-Type": "image/png"}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                self.close()

        with patch.object(mirror, "urlopen", return_value=Response(raw.getvalue())):
            result, ext, mime = mirror.download_image("https://cdn.example/image.png")
        self.assertEqual(ext, ".webp")
        self.assertEqual(mime, "image/webp")
        self.assertEqual(Image.open(io.BytesIO(result)).format, "WEBP")

    def test_localizes_existing_site_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").mkdir()
            (root / "assets/cover.webp").write_bytes(b"local")
            with patch.object(mirror, "ROOT", root):
                self.assertEqual(
                    mirror.local_site_path("https://aninextup.com/assets/cover.webp"),
                    "/assets/cover.webp",
                )

    def test_known_unavailable_sources_use_replacements(self):
        self.assertEqual(
            mirror.SOURCE_OVERRIDES[
                "https://en.dragon-ball-official.com/dragonball/en/news/2026/09/DBSBE_SurgeKV_en.jpg?_=1791070440"
            ],
            "https://dragonball-super.com/en/updates/img/20260903-1.jpg",
        )


if __name__ == "__main__":
    unittest.main()
