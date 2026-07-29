import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "database" / "tomes" / "index.html"
TIER = ROOT / "tier-lists" / "tomes" / "index.html"
BEST = ROOT / "guides" / "best-tomes" / "index.html"
REDIRECTS = ROOT / "_redirects"
SITEMAP = ROOT / "sitemap.xml"


class TomeArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.tier = TIER.read_text(encoding="utf-8")
        cls.best = BEST.read_text(encoding="utf-8")
        cls.redirects = REDIRECTS.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_database_owns_effect_and_unlock_intent(self):
        title = re.search(r"<title>(.*?)</title>", self.hub, re.S).group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", self.hub, re.S).group(1)
        self.assertNotRegex(title.lower(), r"tier list|best tomes")
        self.assertNotRegex(h1.lower(), r"tier list|best tomes")
        self.assertIn("Effect per level", self.hub)
        self.assertIn("Unlock requirement", self.hub)
        schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.hub, re.S)
        self.assertIsNotNone(schema)
        import json
        self.assertEqual(23, json.loads(schema.group(1))["mainEntity"]["numberOfItems"])

    def test_all_tomes_have_table_rows_and_detail_links(self):
        rows = re.findall(
            r'<a class="tome-table-name" href="/database/tomes/([^"]+)">',
            self.hub,
        )
        self.assertEqual(23, len(rows))
        self.assertEqual(23, len(set(rows)))
        for slug in rows:
            self.assertTrue(
                (ROOT / "database" / "tomes" / f"{slug}.html").exists(),
                slug,
            )

    def test_database_cards_do_not_publish_rankings(self):
        self.assertNotRegex(self.hub, r'class="tome-tier')
        self.assertIn('href="/tier-lists/tomes/"', self.hub)
        self.assertIn('href="/database/tomes/"', self.tier)

    def test_old_best_tomes_url_consolidates_to_tier_page(self):
        self.assertIn(
            "/guides/best-tomes /tier-lists/tomes/ 301",
            self.redirects,
        )
        self.assertNotIn(
            "<loc>https://megabonk.org/guides/best-tomes/</loc>",
            self.sitemap,
        )

    def test_tier_page_has_complete_filterable_comparison(self):
        rows = re.findall(
            r'<tr data-tier="[SABC]" data-build="[^"]+" data-unlock="(?:default|unlockable)">',
            self.tier,
        )
        self.assertEqual(23, len(rows))
        table = re.search(
            r'<tbody id="tome-ranking-rows">(.*?)</tbody>',
            self.tier,
            re.S,
        ).group(1)
        links = re.findall(r'href="/database/tomes/([^"]+)"', table)
        self.assertEqual(46, len(links))
        self.assertEqual(23, len(set(links)))
        self.assertIn('id="tome-search"', self.tier)
        self.assertIn('id="build-filter"', self.tier)
        self.assertIn('id="unlock-filter"', self.tier)
        self.assertIn("Showing all 23 Tomes", self.tier)

    def test_tier_comparison_rows_use_local_icons_and_linked_names(self):
        table = re.search(
            r'<tbody id="tome-ranking-rows">(.*?)</tbody>',
            self.tier,
            re.S,
        ).group(1)
        entities = re.findall(
            r'<a class="entity-name-with-icon" href="/database/tomes/([^"]+)"><img src="(/images/database/Tomes/[^"]+)"',
            table,
        )
        self.assertEqual(23, len(entities))
        self.assertEqual(23, len({slug for slug, _ in entities}))
        for _, src in entities:
            self.assertTrue((ROOT / src.lstrip("/")).is_file(), src)
    def test_best_tomes_intent_and_thorns_query_are_merged(self):
        title = re.search(r"<title>(.*?)</title>", self.tier, re.S).group(1)
        self.assertIn("Tome Tier List", title)
        self.assertIn("Best Tomes by Build", title)
        self.assertIn("What are the best Tomes in Megabonk?", self.tier)
        self.assertIn("best Tomes for an Athena Thorns build", self.tier)
        self.assertIn('href="/database/tomes/thorns-tome"', self.tier)

    def test_old_best_page_is_a_redirect_fallback(self):
        self.assertIn(
            "/guides/best-tomes /tier-lists/tomes/ 301",
            self.redirects,
        )
        self.assertIn(
            "/guides/best-tomes/ /tier-lists/tomes/ 301",
            self.redirects,
        )
        self.assertIn('content="noindex, follow"', self.best)
        self.assertIn(
            'rel="canonical" href="https://megabonk.org/tier-lists/tomes/"',
            self.best,
        )
        self.assertIn('url=/tier-lists/tomes/', self.best)
        self.assertNotIn("Tomes Tier List Rankings", self.best)

    def test_internal_links_no_longer_target_old_best_page(self):
        offenders = []
        for page in ROOT.rglob("*.html"):
            if page == BEST:
                continue
            if "/guides/best-tomes" in page.read_text(encoding="utf-8"):
                offenders.append(str(page.relative_to(ROOT)))
        self.assertEqual([], offenders)

    def test_page_metadata_and_source_are_current(self):
        self.assertIn('"dateModified": "2026-07-29"', self.tier)
        self.assertIn("Last Reviewed: July 29, 2026 | Version 1.0.69", self.tier)
        self.assertNotIn("Code injected by live-server", self.tier)
        marker = "<loc>https://megabonk.org/tier-lists/tomes/</loc>"
        start = self.sitemap.index(marker)
        self.assertIn("<lastmod>2026-07-29</lastmod>", self.sitemap[start:start + 180])

    def test_current_luck_value_is_consistent(self):
        luck = (ROOT / "database" / "tomes" / "luck-tome.html").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("+8% Luck", self.hub)
        self.assertNotIn("+8% Luck", self.tier)
        self.assertNotIn("+8% Luck", luck)
        self.assertIn("+7% Luck", self.hub)
        self.assertIn("+7% Luck", self.tier)
        self.assertIn("+7% Luck", luck)
        self.assertIn("Kill 5,000 enemies as Sir Oofie", self.hub)
        self.assertNotIn("Kill 12,500 enemies as Sir Oofie", self.hub)


if __name__ == "__main__":
    unittest.main()
