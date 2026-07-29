"""Normalize Megabonk.org public URLs to Cloudflare Pages clean routes.

Physical files remain ``.html`` on disk. Public flat-page URLs omit the suffix,
while directory ``index.html`` pages keep a trailing slash.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE_PREFIX = "https://megabonk.org"
DIRECTORY_ROUTES = {
    "/" + path.parent.relative_to(ROOT).as_posix()
    for path in ROOT.rglob("index.html")
}
DIRECTORY_ROUTES.add("")
REDIRECT_ROUTES = {}
for line in (ROOT / "_redirects").read_text(encoding="utf-8").splitlines():
    fields = line.split()
    if (
        len(fields) == 3
        and fields[2] == "301"
        and fields[0].startswith("/")
        and fields[1].startswith("/")
        and "*" not in fields[0]
    ):
        REDIRECT_ROUTES[fields[0]] = fields[1]

ABSOLUTE_SITE_URL = re.compile(
    r"https://megabonk\.org/(?P<path>[^\"'<>\s]*)"
)
URL_ATTRIBUTE = re.compile(
    r"(?P<prefix>\b(?:href|action|formaction)\s*=\s*)(?P<quote>[\"'])"
    r"(?P<url>[^\"']+)(?P=quote)",
    re.IGNORECASE,
)
JS_LINK_VALUE = re.compile(
    r"(?P<prefix>\b(?:link|url)\s*:\s*)(?P<quote>[\"'])"
    r"(?P<url>[^\"']+)(?P=quote)",
    re.IGNORECASE,
)


def clean_url(url: str) -> str:
    """Strip .html from a local URL while preserving query strings/fragments."""
    if url.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return url

    if url.startswith(("http://", "https://")):
        if not url.startswith(SITE_PREFIX + "/"):
            return url
        prefix = SITE_PREFIX
        path = url[len(prefix):]
    else:
        prefix = ""
        path = url

    match = re.match(r"(?P<route>[^?#]+)\.html(?P<tail>[?#].*)?$", path)
    if match:
        route = match.group("route")
        tail = match.group("tail") or ""
    else:
        parts = re.match(r"(?P<route>[^?#]+)(?P<tail>[?#].*)?$", path)
        if not parts:
            return url
        route = parts.group("route")
        tail = parts.group("tail") or ""

    changed = bool(match)
    if route == "index":
        route = "./"
        changed = True
    elif route.endswith("/index"):
        route = route[:-len("index")]
        changed = True

    if route.startswith("/") and route.rstrip("/") in DIRECTORY_ROUTES:
        if not route.endswith("/"):
            route += "/"
            changed = True

    if route in REDIRECT_ROUTES:
        route = REDIRECT_ROUTES[route]
        changed = True

    if not changed:
        return url
    return prefix + route + tail


def normalize_html(source: str) -> str:
    source = ABSOLUTE_SITE_URL.sub(
        lambda match: clean_url(match.group(0)),
        source,
    )

    def replace_url(match: re.Match[str]) -> str:
        url = clean_url(match.group("url"))
        return (
            f"{match.group('prefix')}{match.group('quote')}"
            f"{url}{match.group('quote')}"
        )

    source = URL_ATTRIBUTE.sub(replace_url, source)
    return JS_LINK_VALUE.sub(replace_url, source)


def main() -> None:
    changed = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated = normalize_html(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(ROOT).as_posix())

    print(f"Normalized {len(changed)} HTML files.")
    for relative in changed:
        print(relative)


if __name__ == "__main__":
    main()