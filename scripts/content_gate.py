#!/usr/bin/env python3
"""Content gate for v3.20 pages (00 §1.4/§4, 08 format table).

Usage:
  python content_gate.py SITE_ROOT [paths...] [--allow ALLOW.json] [--report-only]
  python content_gate.py --sites PARENT_DIR [--min-sites 2]   (v3.21 cross-site fingerprint report)
  python content_gate.py --theme SITE_ROOT GAME_DIR [GAME_DIR ...] [--report-only]   (v3.22 game theme check)

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
             "config", ".git", "PAGE_REPORTS", "assets", "work", "tests", "fixtures", "tmp", "backup", "backups"}
TRUST = re.compile(r"(?:^|/)(about|contact|privacy|privacy-policy|terms|disclaimer|editorial-policy)(/|\.html$|$)")

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
# v3.21: retelling community posts instead of stating the answer (00 §1.2).
RETELL = [
    r"\b(?:a|one|another|the original|the stuck) (?:player|user|commenter|poster|redditor)s? (?:reports?|says?|said|describes?|points?|suggests?|warns?|claims?|supplied|mentions?)",
    r"\bin a (?:launch-week |recent |separate |late-progress )?(?:reddit|steam|forum|help|discussion) (?:thread|post|reply|discussion)",
    r"\b(?:another|a separate|the player|a single player) (?:report|reply)\b",
    r"\bthe reply (?:points|says|suggests)", r"\bplayer leads?\b", r"\bu/[A-Za-z0-9_-]{3,}",
]
BANNED_H2 = re.compile(r"^((external\s+)?sources?(\s*(&|and)\s*(verification|checks|limits|version|evidence limits|edition limits))?|references|检查依据)$", re.I)

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
    retell = sum(len(re.findall(p, txt, re.I)) for p in RETELL)
    if retell:
        findings.append(("BLOCK", f"retelling community posts x{retell} (state the answer; sources go to FACT_CHECK)"))
    for h2 in re.findall(r"(?is)<h2[^>]*>(.*?)</h2>", main):
        if BANNED_H2.match(text_of(h2)):
            findings.append(("BLOCK", f"sources-style H2: {text_of(h2)}"))
    cites = len(re.findall(r'href="#source-\d+"|<sup[^>]*>\s*<a[^>]+href="#', main))
    if cites:
        findings.append(("BLOCK", f"citation markers x{cites}"))

    ext = []
    # A video's "Watch on YouTube" caption link is creator credit, not an outbound step (08 video rules).
    no_video = re.sub(r'(?is)<figure class="yt-embed">.*?</figure>', "", main)
    for href in re.findall(r'(?i)<a\b[^>]*href="(https?://[^"]+)"', no_video):
        host = urlparse(href).netloc.lower().removeprefix("www.")
        if domain and host.endswith(domain):
            continue
        ext.append(href)
    limits = FORMATS.get(fmt or "other")
    max_ext = allow.get(url, {}).get("max_external", limits[0])
    if len(ext) > max_ext:
        findings.append(("BLOCK", f"external links {len(ext)} > {max_ext} ({len(set(urlparse(e).netloc for e in ext))} domains)"))

    # Video thumbnails are the creator's artwork, not page media (08 video rules, v3.21).
    imgs = len(re.findall(r"(?i)<img\b", re.sub(r'(?is)<button[^>]*class="yt-facade".*?</button>', "", main)))
    min_img = allow.get(url, {}).get("min_images", limits[1])
    if imgs < min_img:
        findings.append(("BLOCK" if fmt else "WARN", f"images {imgs} < {min_img} for format {fmt or 'other'}"))

    # v3.24 alt rules (08): content images need a descriptive, unique alt; filenames are not alt text.
    alts = []
    for tag in re.findall(r"(?i)<img\b[^>]*>", re.sub(r'(?is)<button[^>]*class="yt-facade".*?</button>', "", main)):
        alt = re.search(r'\balt="([^"]*)"', tag)
        if alt is None:
            findings.append(("BLOCK", "img without alt attribute"))
            continue
        a = alt.group(1).strip()
        if a and re.fullmatch(r"[\w\-]+\.(?:png|jpe?g|webp|gif|svg)", a, re.I):
            findings.append(("BLOCK", f"alt is a filename: {a}"))
        if a:
            alts.append(a.lower())
    dup = [a for a in set(alts) if alts.count(a) > 1 and len(a) > 3]
    if dup:
        findings.append(("WARN", f"same alt on several images: {dup[0][:60]}"))

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


def shell_phrases(html):
    """Fixed copy outside the article answer: header/nav/footer text, badges, eyebrow labels."""
    blocks = [m.group(0) for m in re.finditer(r"(?is)<(header|nav|footer)\b.*?</\1>", html)]
    blocks += re.findall(r'(?is)<[^>]+class="[^"]*(?:eyebrow|kicker|badge|tagline|camp-note|site-note)[^"]*"[^>]*>.*?</[a-z0-9]+>', html)
    out = set()
    for b in blocks:
        for seg in re.split(r"[.!?|·•\n]", text_of(strip(b))):
            w = re.sub(r"[^a-z0-9' ]", " ", seg.lower()).split()
            if len(w) >= 3:
                out.add(" ".join(w))
    return out


def cross_sites(parent, min_sites=2):
    """Report shell copy shared by independent domains (00 §3, v3.21)."""
    parent = Path(parent)
    seen = {}
    for site in sorted(d for d in parent.iterdir() if d.is_dir() and "." in d.name and (d / "index.html").exists()):
        name = site.name.lower()
        game = re.split(r"[.-]", name)[0]
        files = [site / "index.html"] + [f for f in list(site.glob("*/index.html"))[:6]]
        for f in files:
            for ph in shell_phrases(f.read_text(encoding="utf-8", errors="ignore")):
                if game[:6] in ph.replace(" ", ""):
                    continue
                seen.setdefault(ph, set()).add(name)
    rows = sorted(((ph, s) for ph, s in seen.items() if len(s) >= min_sites), key=lambda x: -len(x[1]))
    for ph, s in rows[:80]:
        print(f"WARN shared x{len(s)}: \"{ph}\" -> {', '.join(sorted(s)[:6])}{' ...' if len(s) > 6 else ''}")
    print(f"\n{len(rows)} shell phrases shared by >= {min_sites} domains")
    return 0


def theme_check(root, games, report_only=False):
    """Every page under /{game}/ loads /assets/{game}/theme.css and no CSS from another game's asset folder (02 §2.1)."""
    root = Path(root)
    asset_dirs = {d.name for d in (root / "assets").iterdir() if d.is_dir()} if (root / "assets").exists() else set()
    blocks = 0
    for game in games:
        for f in sorted((root / game).rglob("*.html")):
            rel = f.relative_to(root).as_posix()
            if any(p in SKIP_DIRS or p.startswith(".") for p in f.relative_to(root).parts[:-1]):
                continue
            html = f.read_text(encoding="utf-8", errors="ignore")
            if re.search(r'(?i)<meta[^>]+name="robots"[^>]+noindex', html):
                continue
            css = [h.split("?")[0] for h in re.findall(r'<link rel="stylesheet" href="([^"]+)"', html)]
            issues = []
            if f"/assets/{game}/theme.css" not in css:
                issues.append(f"missing /assets/{game}/theme.css")
            foreign = [c for c in css if c.startswith("/assets/") and c.split("/")[2] in asset_dirs and c.split("/")[2] != game]
            if foreign:
                issues.append("loads other games' CSS: " + ", ".join(foreign))
            if issues:
                blocks += 1
                print(f"/{rel}")
                for i in issues:
                    print(f"  BLOCK: {i}")
    print(f"\ntheme check: {blocks} pages with BLOCK findings")
    return 0 if report_only or not blocks else 1


def main():
    args = [a for a in sys.argv[1:]]
    if "--theme" in args:
        rest = [a for a in args if not a.startswith("--")]
        sys.exit(theme_check(rest[0], rest[1:], "--report-only" in args))
    if "--sites" in args:
        i = args.index("--sites")
        ms = int(args[args.index("--min-sites") + 1]) if "--min-sites" in args else 2
        sys.exit(cross_sites(args[i + 1], ms))
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
            if TRUST.search(f.relative_to(root).as_posix()):
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
