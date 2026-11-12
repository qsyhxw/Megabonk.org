#!/usr/bin/env python3
"""Content gate for v3.20 pages (00 §1.4/§4, 08 format table).

Usage:
  python content_gate.py SITE_ROOT [paths...] [--allow ALLOW.json] [--report-only]

- SITE_ROOT: project root (public files live here).
- paths: optional list of HTML files (relative to SITE_ROOT) to check; default = all
  public index.html / *.html excluding _private, node_modules, dist, build, outputs,
  scripts, src, config, and trust/404 pages.
- --allow: JSON {"/url/path/": {"max_external": 6, "reason": "..."}} for recorded exceptions.
- --report-only: always exit 0 (use for audits of old pages).

Exit code 1 when any checked page has a BLOCK finding.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SKIP_DIRS = {"_private", "node_modules", "dist", "build", "outputs", "scripts", "src",
             "config", ".git", "PAGE_REPORTS", "assets"}
TRUST = re.compile(r"^(about|contact|privacy|terms|disclaimer|editorial-policy)(/|$)")

BANNED = [
    r"not tested by this site", r"we have not (?:personally )?tested", r"no gameplay test",
    r"no hands-on test", r"no claim of hands-on", r"source-based (?:guide|guidance)",
    r"does not claim an independent playtest", r"community reports describe",
    r"one reported route", r"decision framework", r"this checklist is our",
    r"not an official tier list", r"what this guide does not rank",
    r"source changes detected", r"editorial recommendations are awaiting review",
    r"automatic checks do not validate", r"external site, opens in a new tab",
    r"\(opens in a new tab\)", r"未实测", r"本站未(?:实际)?测试",
]
BANNED_H2 = re.compile(r"^(sources?\s*(&|and)\s*(verification|checks|evidence limits)|references|检查依据)$", re.I)

# format -> (max external links, min images, first-screen check)
FORMATS = {
    "codes": (2, 1, "table"), "build": (2, 8, "loadout"), "tier": (2, 10, "tier-grid"),
    "database": (2, 1, "filter"), "entry": (2, 1, "table"), "location": (2, 2, "img"),
    "fix": (2, 1, "ol"), "platform": (3, 1, "table"), "beginner": (2, 3, "ol"),
    "hub": (3, 6, "hub"), "play": (3, 1, None), "other": (3, 1, None),
}


def strip(html, tags=("script", "style", "svg", "noscript")):
    for t in tags:
        html = re.sub(rf"(?is)<{t}\b.*?</{t}>", " ", html)
    return html


def main_block(html):
    m = re.search(r"(?is)<main\b.*?</main>", html)
    if m:
        return m.group(0)
    body = re.sub(r"(?is)<(header|nav|footer)\b.*?</\1>", " ", html)
    return body


def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    t = re.sub(r"&nbsp;|&#160;", " ", t)
    t = re.sub(r"&amp;", "&", t)
    return re.sub(r"\s+", " ", t).strip()


def check(path, root, domain, allow):
    rel = path.relative_to(root).as_posix()
    url = "/" + re.sub(r"(index)?\.html$", "", rel)
    html = path.read_text(encoding="utf-8", errors="ignore")
    if re.search(r'(?i)<meta[^>]+name="robots"[^>]+noindex', html):
        return url, None, []
    body = strip(html)
    main = main_block(body)
    fmt_m = re.search(r'<body[^>]*data-format="([a-z-]+)"', html)
    fmt = fmt_m.group(1) if fmt_m else None
    findings = []

    txt = text_of(main)
    for pat in BANNED:
        n = len(re.findall(pat, txt, re.I))
        if n:
            findings.append(("BLOCK", f"banned phrase x{n}: /{pat}/"))
    for h2 in re.findall(r"(?is)<h2[^>]*>(.*?)</h2>", main):
        if BANNED_H2.match(text_of(h2)):
            findings.append(("BLOCK", f"sources-style H2: {text_of(h2)}"))
    cites = len(re.findall(r'href="#source-\d+"|<sup[^>]*>\s*<a[^>]+href="#', main))
    if cites:
        findings.append(("BLOCK", f"citation markers x{cites}"))

    ext = []
    for href in re.findall(r'(?i)<a\b[^>]*href="(https?://[^"]+)"', main):
        host = urlparse(href).netloc.lower().removeprefix("www.")
        if domain and host.endswith(domain):
            continue
        ext.append(href)
    limits = FORMATS.get(fmt or "other")
    max_ext = allow.get(url, {}).get("max_external", limits[0])
    if len(ext) > max_ext:
        findings.append(("BLOCK", f"external links {len(ext)} > {max_ext} ({len(set(urlparse(e).netloc for e in ext))} domains)"))

    imgs = len(re.findall(r"(?i)<img\b", main))
    min_img = allow.get(url, {}).get("min_images", limits[1])
    if imgs < min_img:
        findings.append(("BLOCK" if fmt else "WARN", f"images {imgs} < {min_img} for format {fmt or 'other'}"))

    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", body)
    if not h1:
        findings.append(("BLOCK", "missing H1"))

    first = re.split(r"(?i)<h2\b", main, maxsplit=1)[0]
    need = limits[2]
    if need == "table" and "<table" not in first.lower():
        findings.append(("WARN", "no table before first H2"))
    elif need == "ol" and "<ol" not in first.lower():
        findings.append(("WARN", "no ordered steps before first H2"))
    elif need == "img" and "<img" not in first.lower():
        findings.append(("WARN", "no image before first H2"))
    elif need in ("loadout", "tier-grid") and need not in first:
        findings.append(("WARN", f"no .{need} before first H2"))
    elif need == "filter" and not re.search(r"(?i)<input|<select", main):
        findings.append(("WARN", "no search/filter control"))
    elif need == "hub":
        cards = len(re.findall(r'(?i)<a\b[^>]*href="/[^"]*"', first))
        if cards < 6:
            findings.append(("WARN", f"hub first screen has {cards} internal entries (<6)"))

    if not fmt:
        findings.append(("WARN", "no data-format on <body> (08)"))
    dated = len(re.findall(r"(?i)\b(checked|verified)\b[^.]{0,40}\b20\d\d\b", txt))
    if dated > 1:
        findings.append(("WARN", f"{dated} 'checked <date>' lines (keep one Updated line)"))
    return url, fmt, findings


def main():
    args = [a for a in sys.argv[1:]]
    report_only = "--report-only" in args
    allow = {}
    if "--allow" in args:
        i = args.index("--allow")
        allow = json.loads(Path(args[i + 1]).read_text(encoding="utf-8"))
        del args[i:i + 2]
    args = [a for a in args if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    root = Path(args[0]).resolve()
    domain = root.name.lower().removeprefix("www.")
    if args[1:]:
        files = [root / p for p in args[1:]]
    else:
        files = []
        for f in root.rglob("*.html"):
            parts = f.relative_to(root).parts
            if any(p in SKIP_DIRS or p.startswith(".") for p in parts[:-1]) or f.name == "404.html":
                continue
            if TRUST.match(f.relative_to(root).as_posix()):
                continue
            files.append(f)
    blocks = 0
    summary = {}
    for f in sorted(files):
        url, fmt, findings = check(f, root, domain, allow)
        if not findings:
            continue
        for level, msg in findings:
            key = re.sub(r"(?<![A-Za-z])\d+", "N", msg.split(":")[0] if "phrase" in msg else msg)
            key = re.sub(r"\(.*?\)", "", key).strip()
            summary[key] = summary.get(key, 0) + 1
        if any(l == "BLOCK" for l, _ in findings):
            blocks += 1
        print(f"{url} [{fmt or '-'}]")
        for level, msg in findings:
            print(f"  {level}: {msg}")
    print(f"\nchecked {len(files)} pages; {blocks} with BLOCK findings")
    for k, v in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {v:4d}  {k}")
    sys.exit(0 if report_only or blocks == 0 else 1)


if __name__ == "__main__":
    main()
