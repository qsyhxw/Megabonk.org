import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDS = ROOT / "guides" / "builds"
SITEMAP = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
NON_CANONICAL_BUILD_PAGES = {
    "gigachad-best-build/index.html",
    "knight-best-build/index.html",
    "skeleton-best-build/index.html",
    "zorro-best-build/index.html",
}


def build_pages():
    flat = BUILDS.glob("*-best-build.html")
    nested = BUILDS.glob("*-best-build/index.html")
    pages = [*flat, *nested]
    return sorted(
        page for page in pages
        if page.relative_to(BUILDS).as_posix() not in NON_CANONICAL_BUILD_PAGES
    )


def expected_character_id(path: Path) -> str:
    slug = path.stem if path.name != "index.html" else path.parent.name
    slug = slug.removesuffix("-best-build")
    return slug.replace("-", "")


class CharacterBuildSignalPageTests(unittest.TestCase):
    def test_every_canonical_best_build_page_loads_the_dynamic_module_once(self):
        pages = build_pages()
        self.assertEqual(len(pages), 21)

        for page in pages:
            with self.subTest(page=page.relative_to(ROOT)):
                source = page.read_text(encoding="utf-8")
                character_id = expected_character_id(page)
                self.assertEqual(source.count("character-build-signals.css"), 1)
                self.assertEqual(source.count("entity-catalog.js"), 1)
                self.assertEqual(source.count("character-build-signals.js"), 1)
                self.assertEqual(
                    len(
                        re.findall(
                            rf'data-character-build-signals="{re.escape(character_id)}"',
                            source,
                        )
                    ),
                    1,
                )
                self.assertLess(source.index("<h1"), source.index("data-character-build-signals="))
                self.assertLess(source.index("entity-catalog.js"), source.index("character-build-signals.js"))
                self.assertIn(
                    '<meta property="article:modified_time" content="2026-07-29T00:00:00+08:00">',
                    source,
                )
                self.assertIn('data-editorial-reviewed="July 29, 2026"', source)
                canonical = re.search(
                    r'<link rel="canonical" href="([^"]+)"\s*/?>', source
                ).group(1)
                self.assertRegex(
                    SITEMAP,
                    rf'<loc>{re.escape(canonical)}</loc>\s*<lastmod>2026-07-29</lastmod>',
                )

    def test_signal_renderer_resolves_source_character_aliases(self):
        source = (ROOT / "js" / "character-build-signals.js").read_text(
            encoding="utf-8"
        )
        self.assertIn("characterEntry.id === signalEntry.id", source)
        self.assertIn("encodeURIComponent(signal.character)", source)
        self.assertIn("early, mid and late-run sections", source)
        self.assertIn("characterEntry?.page", source)
        self.assertIn("Editorial review:", source)

        styles = (ROOT / "css" / "character-build-signals.css").read_text(
            encoding="utf-8"
        )
        self.assertIn(".cbs-usage-note", styles)
        self.assertIn(".nav-links { display: none !important; }", styles)
        self.assertIn("overflow-x: auto", styles)


if __name__ == "__main__":
    unittest.main()
