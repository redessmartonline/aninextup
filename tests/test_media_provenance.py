"""Regression checks for preserving provenance and independently reviewed rights."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

class RightsEvidenceTests(unittest.TestCase):
    def test_mirroring_keeps_source_credit_links_external(self):
        mirror = module("mirror_site_images")
        url = "https://example.org/a.jpg"
        source = f'<figure><img src="{url}"><figcaption>Source: <a href="{url}">Owner</a></figcaption></figure>'
        result = mirror.rewrite_image_urls(source, {url: "/assets/a.webp"})
        self.assertIn('<img src="/assets/a.webp">', result)
        self.assertIn(f'<a href="{url}">', result)

    def test_empty_mirror_run_does_not_erase_historical_source(self):
        mirror = module("mirror_site_images")
        old = {"images": [{"source": "https://example.org/a.jpg", "local": "/assets/a.webp", "evidence_commit": "known"}]}
        self.assertEqual(mirror.merge_source_history(old, {}), old["images"])
        merged = mirror.merge_source_history(old, {"https://example.org/a.jpg": "/assets/a.webp", "https://example.org/b.jpg": "/assets/b.webp"})
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]["evidence_commit"], "known")

    def test_provenance_does_not_grant_permission_and_review_survives_rebuild(self):
        register = module("build_image_rights_register")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "articles").mkdir()
            (root / "assets/images/external").mkdir(parents=True)
            (root / "audits").mkdir()
            (root / "articles/a.html").write_text('<figure><img src="../assets/a.webp"><figcaption>Owner credit</figcaption></figure>')
            (root / "assets/images/external/sources.json").write_text(json.dumps({"images": [{"source": "https://example.org/a.jpg", "local": "/assets/a.webp"}]}))
            first = register.build(root)[0]
            self.assertEqual(first["permission_status"], "UNVERIFIED")
            self.assertTrue(first["provenance"])
            decision = {"permission_status": "DOCUMENTED_PERMISSION", "rights_holder": "Example owner", "permission_scope": "Specific editorial reuse", "license_evidence": ["https://example.org/permission"]}
            (root / "audits/media-permissions.json").write_text(json.dumps({"assets": {"/assets/a.webp": decision}}))
            second = register.build(root)[0]
            self.assertEqual(second["license_evidence"], decision["license_evidence"])
            self.assertEqual(second["permission_status"], "DOCUMENTED_PERMISSION")
            decision["license_evidence"] = []
            (root / "audits/media-permissions.json").write_text(json.dumps({"assets": {"/assets/a.webp": decision}}))
            with self.assertRaises(ValueError):
                register.build(root)

if __name__ == "__main__":
    unittest.main()
