import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuildAliasConsolidationTests(unittest.TestCase):
    redirects = {
        "gigachad-best-build": "/guides/builds/megachad-best-build",
        "knight-best-build": "/guides/builds/sir-oofie-best-build",
        "skeleton-best-build": "/guides/builds/calcium-best-build",
    }

    def test_retired_aliases_redirect_and_use_safe_fallbacks(self):
        rules = (ROOT / "_redirects").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for slug, destination in self.redirects.items():
            route = f"/guides/builds/{slug}"
            self.assertIn(f"{route} {destination} 301", rules)
            self.assertIn(f"{route}/* {destination} 301", rules)
            self.assertNotIn(f"https://megabonk.org{route}/</loc>", sitemap)

            source = (ROOT / "guides" / "builds" / slug / "index.html").read_text(
                encoding="utf-8"
            )
            self.assertIn('content="noindex,follow"', source)
            self.assertIn(f'href="https://megabonk.org{destination}"', source)
            self.assertIn(f'content="0; url={destination}"', source)

    def test_alias_content_is_merged_into_primary_build_pages(self):
        expected_sections = {
            "guides/builds/megachad-best-build.html": 'id="gigachad-alias"',
            "guides/builds/sir-oofie-best-build.html": 'id="knight-beginner-route"',
            "guides/builds/calcium-best-build.html": 'id="skeleton-speed-demon"',
        }
        for relative_path, marker in expected_sections.items():
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(marker, source)

    def test_no_internal_html_links_target_retired_aliases(self):
        retired_sources = {
            ROOT / "guides" / "builds" / slug / "index.html"
            for slug in self.redirects
        }
        old_routes = tuple(f"/guides/builds/{slug}" for slug in self.redirects)
        offenders = []
        for path in ROOT.rglob("*.html"):
            if path in retired_sources or "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8", errors="ignore")
            if any(route in source for route in old_routes):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_zorro_page_owns_alias_intent_not_generic_build_intent(self):
        source = (
            ROOT / "guides" / "builds" / "zorro-best-build" / "index.html"
        ).read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", source, re.DOTALL).group(1)
        description = re.search(
            r'<meta name="description" content="(.*?)">', source, re.DOTALL
        ).group(1)
        self.assertLessEqual(len(title), 60)
        self.assertLessEqual(len(description), 160)
        self.assertEqual(source.count("<h1>"), 1)
        self.assertIn("Who Is Zorro in Megabonk?", source)
        self.assertIn('href="/guides/builds/bandit-best-build"', source)
        self.assertNotIn("data-character-build-signals", source)
        self.assertNotIn("character-build-signals.js", source)

        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', source, re.DOTALL
        )
        self.assertGreaterEqual(len(scripts), 3)
        for script in scripts:
            json.loads(script)


if __name__ == "__main__":
    unittest.main()