import importlib.util
import json
import sys
import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "patch_updater", ROOT / "scripts" / "update_patch_notes.py"
)
patch_updater = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = patch_updater
SPEC.loader.exec_module(patch_updater)


class PatchNotesUpdaterTests(unittest.TestCase):
    def make_workspace(self):
        temp_root = Path("C:/tmp") if os.name == "nt" and Path("C:/tmp").exists() else ROOT
        temporary = tempfile.TemporaryDirectory(dir=temp_root)
        root = Path(temporary.name)
        page = root / "guides" / "patch-notes" / "index.html"
        sitemap = root / "sitemap.xml"
        state = root / "data" / "patch-notes-state.json"
        page.parent.mkdir(parents=True)
        state.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "guides" / "patch-notes" / "index.html", page)
        shutil.copy2(ROOT / "sitemap.xml", sitemap)
        shutil.copy2(ROOT / "data" / "patch-notes-state.json", state)
        return temporary, page, sitemap, state

    def load_fixture(self, name):
        path = ROOT / "tests" / "fixtures" / name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_current_official_data_does_not_rewrite_page(self):
        temporary, page, sitemap, state = self.make_workspace()
        self.addCleanup(temporary.cleanup)
        original_page = page.read_text(encoding="utf-8")
        payload = self.load_fixture("steam-news-current.json")
        fixture_latest = max(
            patch_updater.parse_official_news(payload),
            key=lambda record: patch_updater.version_key(record.version),
        )
        seeded_state = json.loads(state.read_text(encoding="utf-8"))
        seeded_state["versions"][fixture_latest.version]["source_hash"] = (
            fixture_latest.source_hash
        )
        state.write_text(json.dumps(seeded_state), encoding="utf-8")

        result = patch_updater.run_update(
            payload,
            page,
            sitemap,
            state,
            date(2026, 7, 23),
        )

        self.assertFalse(result["page_changed"])
        self.assertEqual(result["new_versions"], [])
        self.assertEqual(page.read_text(encoding="utf-8"), original_page)
        saved = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(saved["latest_version"], "1.0.69")
        self.assertTrue(saved["versions"]["1.0.69"]["source_hash"])

    def test_new_version_updates_page_sitemap_and_is_idempotent(self):
        temporary, page, sitemap, state = self.make_workspace()
        self.addCleanup(temporary.cleanup)
        payload = self.load_fixture("steam-news-new.json")

        first = patch_updater.run_update(
            payload, page, sitemap, state, date(2026, 8, 2)
        )
        rendered = page.read_text(encoding="utf-8")
        rendered_sitemap = sitemap.read_text(encoding="utf-8")
        rendered_state = state.read_text(encoding="utf-8")

        self.assertTrue(first["page_changed"])
        self.assertEqual(first["new_versions"], ["1.0.70"])
        self.assertIn('<meta name="patch-version" content="1.0.70">', rendered)
        self.assertIn("Megabonk Patch Notes V1.0.70", rendered)
        self.assertIn('data-patch-version="1.0.70"', rendered)
        self.assertIn('id="v1070"', rendered)
        self.assertIn("2026-08-02</lastmod>", rendered_sitemap)

        second = patch_updater.run_update(
            payload, page, sitemap, state, date(2026, 8, 2)
        )
        self.assertFalse(second["page_changed"])
        self.assertEqual(page.read_text(encoding="utf-8"), rendered)
        self.assertEqual(sitemap.read_text(encoding="utf-8"), rendered_sitemap)
        self.assertEqual(state.read_text(encoding="utf-8"), rendered_state)

    def test_non_official_items_are_rejected(self):
        payload = self.load_fixture("steam-news-new.json")
        payload["appnews"]["newsitems"][0]["feedname"] = "steam_community"
        with self.assertRaises(patch_updater.UpdateError):
            patch_updater.parse_official_news(payload)


if __name__ == "__main__":
    unittest.main()
