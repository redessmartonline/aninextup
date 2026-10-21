import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class AnalyticsInstallation(unittest.TestCase):
    def test_missing_tag_is_a_failed_preflight(self):
        source = (ROOT / "articles/eleceed-anime-april-2027-release-date.html").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eleceed-anime-april-2027-release-date.html"
            path.write_text(source.replace("googletagmanager.com/gtag/js?id=G-TRV5CF738D", "missing-analytics.js"))
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/audit_all_articles_preflight.py"), "--root", tmp, "--out", str(Path(tmp) / "report")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing_ga4_tag", result.stdout)

    def test_each_live_article_has_one_installation(self):
        for path in (ROOT / "articles").glob("*.html"):
            with self.subTest(article=path.name):
                self.assertEqual(path.read_text().count("googletagmanager.com/gtag/js?id=G-TRV5CF738D"), 1)


if __name__ == "__main__":
    unittest.main()
