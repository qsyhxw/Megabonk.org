import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_PREFIX = "https://megabonk.org"
DIRECTORY_ROUTES = {
    "/" + path.parent.relative_to(ROOT).as_posix()
    for path in ROOT.rglob("index.html")
}
DIRECTORY_ROUTES.add("")
REDIRECT_ROUTES = {
    fields[0]
    for line in (ROOT / "_redirects").read_text(encoding="utf-8").splitlines()
    if len(fields := line.split()) == 3
    and fields[2] == "301"
    and fields[0].startswith("/")
    and "*" not in fields[0]
}


class UrlSuffixPolicyTests(unittest.TestCase):
    def test_sitemap_uses_only_clean_public_urls(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text or "" for node in tree.findall(".//sm:loc", namespace)]
        self.assertTrue(urls)
        self.assertFalse(
            [url for url in urls if re.search(r"\.html(?:$|[?#])", url)],
            "Sitemap must not submit redirecting .html URLs.",
        )
        self.assertEqual(len(urls), len(set(urls)))
        submitted_routes = {url.removeprefix(SITE_PREFIX) for url in urls}
        self.assertFalse(
            submitted_routes & REDIRECT_ROUTES,
            "Sitemap must not submit URLs that immediately 301.",
        )

    def test_pages_use_clean_canonical_and_hreflang_urls(self):
        violations = []
        for path in ROOT.rglob("*.html"):
            source = path.read_text(encoding="utf-8")
            for tag in re.findall(r"<link\b[^>]+>", source, re.IGNORECASE):
                if not re.search(
                    r"\brel=[\"'](?:canonical|alternate)[\"']", tag,
                    re.IGNORECASE,
                ):
                    continue
                if re.search(r"\bhref=[\"'][^\"']+\.html(?:[?#][^\"']*)?[\"']", tag):
                    violations.append(path.relative_to(ROOT).as_posix())
        self.assertFalse(
            violations,
            f"Canonical/hreflang URLs must use clean routes: {violations}",
        )

    def test_internal_links_do_not_create_html_redirect_hops(self):
        violations = []
        patterns = (
            re.compile(
                r"\b(?:href|action|formaction)\s*=\s*[\"'](?P<url>[^\"']+)[\"']",
                re.IGNORECASE,
            ),
            re.compile(
                r"\b(?:link|url)\s*:\s*[\"'](?P<url>[^\"']+)[\"']",
                re.IGNORECASE,
            ),
        )
        for path in ROOT.rglob("*.html"):
            source = path.read_text(encoding="utf-8")
            for pattern in patterns:
                for match in pattern.finditer(source):
                    url = match.group("url")
                    if url.startswith(("http://", "https://")) and not url.startswith(
                        SITE_PREFIX + "/"
                    ):
                        continue
                    route = url.split("#", 1)[0].split("?", 1)[0]
                    route_without_origin = route.removeprefix(SITE_PREFIX)
                    if (
                        route.endswith(".html")
                        or route_without_origin == "index"
                        or route_without_origin.endswith("/index")
                        or (
                            route_without_origin.startswith("/")
                            and route_without_origin.rstrip("/") in DIRECTORY_ROUTES
                            and not route_without_origin.endswith("/")
                        )
                        or route_without_origin in REDIRECT_ROUTES
                    ):
                        violations.append(
                            f"{path.relative_to(ROOT).as_posix()} -> {url}"
                        )
        self.assertFalse(
            violations,
            "Internal links must point directly to clean routes:\n"
            + "\n".join(violations[:30]),
        )

    def test_sitemap_excludes_noindex_pages(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text or "" for node in tree.findall(".//sm:loc", namespace)}
        for path in ROOT.rglob("*.html"):
            source = path.read_text(encoding="utf-8")
            if not re.search(
                r'<meta[^>]+name=["'']robots["''][^>]+content=["''][^"'']*noindex',
                source,
                re.IGNORECASE,
            ):
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative == "index.html":
                route = "/"
            elif relative.endswith("/index.html"):
                route = "/" + relative[:-len("index.html")]
            else:
                route = "/" + relative[:-len(".html")]
            self.assertNotIn(SITE_PREFIX + route, urls, relative)

    def test_sitemap_urls_match_page_canonicals(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for node in tree.findall(".//sm:loc", namespace):
            url = node.text or ""
            route = url.removeprefix(SITE_PREFIX)
            if route == "/":
                path = ROOT / "index.html"
            elif route.endswith("/"):
                path = ROOT / route.lstrip("/") / "index.html"
            else:
                path = ROOT / f"{route.lstrip('/')}.html"
            self.assertTrue(path.is_file(), url)
            source = path.read_text(encoding="utf-8")
            canonical = re.search(
                r'<link[^>]+rel=["'']canonical["''][^>]+href=["'']([^"'']+)["'']',
                source,
                re.IGNORECASE,
            )
            self.assertIsNotNone(canonical, path.relative_to(ROOT).as_posix())
            self.assertEqual(url, canonical.group(1), path.relative_to(ROOT).as_posix())

    def test_sitemap_generator_encodes_the_same_policy(self):
        source = (ROOT / "generate_sitemap.py").read_text(encoding="utf-8")
        self.assertIn("def public_path(rel_path):", source)
        self.assertIn("rel_path[:-len('.html')]", source)
        self.assertNotIn("canonical_overrides", source)

    def test_pages_list_uses_clean_urls(self):
        listed = {
            line.strip()
            for line in (ROOT / "pages_list.txt").read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        self.assertFalse(
            [url for url in listed if re.search(r"\.html(?:$|[?#])", url)]
        )
        tree = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = {
            node.text or "" for node in tree.findall(".//sm:loc", namespace)
        }
        self.assertEqual(sitemap_urls, listed)


if __name__ == "__main__":
    unittest.main()