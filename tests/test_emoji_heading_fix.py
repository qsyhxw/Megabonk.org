import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "js" / "current-year.js"

class EmojiHeadingFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_shared_script_wraps_leading_emoji(self):
        for token in (
            "Extended_Pictographic",
            "Intl.Segmenter",
            "leading-emoji-icon",
            "emojiHeadingFixed",
            "MutationObserver",
        ):
            self.assertIn(token, self.script)

    def test_gradient_pages_load_shared_fix(self):
        missing = []
        for page in ROOT.rglob("*.html"):
            rel = page.relative_to(ROOT).as_posix()
            if rel.startswith("components/"):
                continue
            html = page.read_text(encoding="utf-8")
            has_gradient = bool(re.search(r"-webkit-text-fill-color\s*:\s*transparent|background-clip\s*:\s*text", html))
            if has_gradient and "</body>" in html and "/js/current-year.js?v=20260728" not in html:
                missing.append(rel)
        self.assertEqual([], missing)

    def test_shared_script_is_not_duplicated(self):
        duplicates = []
        for page in ROOT.rglob("*.html"):
            html = page.read_text(encoding="utf-8")
            if html.count("/js/current-year.js") > 1:
                duplicates.append(page.relative_to(ROOT).as_posix())
        self.assertEqual([], duplicates)

if __name__ == "__main__":
    unittest.main()
