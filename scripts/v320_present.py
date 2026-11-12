#!/usr/bin/env python3
"""v3.20 presentation pass for already generated static pages (00 §1.4, §4).

Usage:
  python v320_present.py SITE_ROOT [--dry-run] [paths...]

Idempotent. Edits final public HTML in place:
- removes public Sources/References sections and [n] citation markers
  (evidence stays in the site's FACT_CHECK / data / generator sources);
- removes "opens in a new tab" screen-reader sentences and evidence-status
  boilerplate ("not tested by this site", "source-based guide", ...);
- unwraps evidence-only outbound links (community threads, wikis, other guide
  sites, videos) to plain text and keeps action links (store, download,
  workshop, mod hosts, Discord, official site) once per page;
- never touches <head>, header, footer, nav, scripts, figcaptions or trust/404 pages.

Run after the site's normal generator, then run content_gate.py.
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SKIP_DIRS = {"_private", "node_modules", "dist", "build", "outputs", "scripts", "src",
             "config", "assets", "PAGE_REPORTS", "data", "tools", "templates", "work", "tests", "fixtures", "tmp", "backup", "backups"}
TRUST = re.compile(r"^(about|contact|privacy|terms|disclaimer|editorial-policy)(/|$)")

SOURCE_HEAD = re.compile(
    r"<h[23][^>]*>\s*(?:<[^>]+>\s*)*(?:(?:External\s+)?Sources?(?:\s*(?:&amp;|&|and)\s*(?:verification|checks|limits|version|evidence(?: limits)?|edition limits|notes))?(?:\s+for\s+[^<]{1,60})?|"
    r"References?|Sources for this update|Evidence boundary|检查依据|来源与核对|出典[^<]{0,10}|Fontes(?: e verificação)?|"
    r"Quellen|Fuentes(?: y comprobaciones)?|Источники(?: и (?:проверка|ограничения))?|출처[^<]{0,12}|來源[^<]{0,8}|出處[^<]{0,8}|来源[^<]{0,8}|情報源[^<]{0,8}|Quellen[^<]{0,20}|Fuentes[^<]{0,24}|Fontes[^<]{0,24})\s*(?:<[^>]+>\s*)*</h[23]>",
    re.I)
CITE = re.compile(r'<sup\b[^>]*>\s*(?:<a\b[^>]*href="#[^"]*"[^>]*>.*?</a>\s*)+</sup>', re.S)
CITE_A = re.compile(r'<a\b[^>]*class="[^"]*\breference\b[^"]*"[^>]*href="#[^"]*"[^>]*>.*?</a>', re.S)
NEWTAB = re.compile(r'<span class="(?:sr-only|visually-hidden)">\s*\(?[^<()]*(?:new tab|new window)[^<()]*\)?\s*</span>', re.I)
TOC_SOURCES = re.compile(r'<li>\s*<a href="#(?:sources?|references?|sources-[a-z-]+)"[^>]*>[^<]*</a>\s*</li>|<a href="#(?:sources?|references?)"[^>]*>[^<]*</a>', re.I)
DANGLING = re.compile(r'<a\b[^>]*href="#(?:source|ref|cite|fn)[-_a-z]*\d+"[^>]*>(.*?)</a>', re.S | re.I)

HEDGE = [
    # Whole sentences whose only content is our test status (no player action).
    r"\s*(?:This is (?:an editorial |a )?source-based (?:guide|guidance)[^.<]{0,120}|This is an editorial decision framework[^.<]{0,140}|"
    r"We have not (?:personally )?tested (?:it|this|these|them|the mode|the routes?|the dungeon|this dungeon|either branch|"
    r"these builds(?: or troubleshooting steps)?|the vocations|this guide|this build)[^.<]{0,40}|"
    r"Source review; no gameplay test by this site|No gameplay test is claimed|"
    r"Recommendations combine published class descriptions with player preferences; we have not personally tested the vocations)\.",
    r"\s*[;,]?\s*we have not (?:personally )?tested (?:them|it|this|that on your server)\.",
    r"<span[^>]*>\s*Source-based guide\s*</span>",
    r"\s*Source-based guide(?=\s*(?:<[^>]+>\s*)*Checked)",

    r"\s*Checked [A-Z][a-z]+ \d{1,2}, 20\d\d; not tested by this site\.",
    r"\s*Checked \d{1,2} [A-Z][a-z]+ 20\d\d; not tested by this site\.",
    r";?\s*not tested by this site\.?",
    r"\s*We have not personally tested (?:the game or )?(?:the fixes on this page|these steps|these setups or fixes|this)\.",
    r"\s*Research-based guidance; we have not personally tested these setups or fixes\.",
    r"\s*This site does not claim an independent playtest\.",
    r"\s*No claim of hands-on testing\.",
    r"\s*These notes separate developer rules from player reports\.",
    r"\s*External originals open in a new tab\.",
    r"\s*Source-based guidance checked \d{1,2} [A-Z][a-z]+ 20\d\d\.",
    r"\s*·\s*Source-based (?:guide|guidance)",
    r"\s*Source-based (?:guide|guidance)\s*·",
    r"\s*·\s*No (?:new )?(?:full-run|gameplay|hands-on) test",
    r"\s*No [^.<]{0,60}(?:was|were|has been|have been) tested by this site\.",
    r"\s*[^.<]{0,40}not (?:independently )?tested here\.",
]

# Evidence-only hosts: readers should not need to leave to finish the task.
EVIDENCE_HOSTS = re.compile(
    r"(?:^|\.)(?:reddit\.com|redd\.it|fandom\.com|wiki\.gg|fextralife\.com|game8\.co|powerpyx\.com|allthings\.how|"
    r"gamerant\.com|thegamer\.com|ign\.com|pcgamer\.com|rockpapershotgun\.com|pcgamesn\.com|eurogamer\.net|"
    r"gamesradar\.com|polygon\.com|dexerto\.com|sportskeeda\.com|gamepressure\.com|steamdb\.info|steamcharts\.com|"
    r"youtube\.com|youtu\.be|twitch\.tv|x\.com|twitter\.com|facebook\.com|tiktok\.com|instagram\.com|"
    r"bsky\.app|threads\.net|medium\.com|wikipedia\.org|archive\.org|web\.archive\.org|virustotal\.com|"
    r"docs\.virustotal\.com|pocketgamer\.com|gamesindustry\.biz|insider-gaming\.com|videogameschronicle\.com|"
    r"gamewith\.jp|game8\.jp|pockettactics\.com|destructoid\.com|mlbbhub\.com|wikitactics\.com|howtofishgame\.wiki|"
    r"planet\.hoyoverse\.com|lootbar\.com|developers\.cloudflare\.com|nvidia\.com|theymes\.com)$")
EVIDENCE_PATHS = re.compile(r"steamcommunity\.com/(?!sharedfiles|workshop)|"
                            r"itch\.io/(?:post|t/|devlog|blog)|/devlog/|/news/|/newslist/|/blog/|/game-updates/|/hc/[a-z-]+/articles/|"
                            r"wiki\.[a-z0-9-]+\.com/|"
                            r"store\.steampowered\.com/news|steamcommunity\.com/games/\d+/announcements|"
                            r"/assets/[^\"]*\.js|/version\.json")


def balanced_section(html, start):
    """Return end index of the <section> opened at start (handles nesting)."""
    depth, i = 0, start
    tag = re.compile(r"<(/?)(section|aside|div)\b[^>]*>", re.I)
    opener = tag.match(html, start).group(2).lower()
    for m in tag.finditer(html, start):
        if m.group(2).lower() != opener:
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    return -1


def drop_source_sections(main):
    out, pos = [], 0
    for m in re.finditer(r"<(section|aside|div)\b[^>]*>", main, re.I):
        if m.start() < pos:
            continue
        end = balanced_section(main, m.start())
        if end < 0:
            continue
        block = main[m.start():end]
        head = block[:600]
        if SOURCE_HEAD.search(head) and len(re.findall(r"<h2\b", block, re.I)) <= 1:
            out.append(main[pos:m.start()])
            pos = end
    out.append(main[pos:])
    return "".join(out)


def is_evidence(url):
    p = urlparse(url)
    host = p.netloc.lower().split(":")[0]
    return bool(EVIDENCE_HOSTS.search(host) or EVIDENCE_PATHS.search(url))


def unwrap_links(main, domain):
    seen = set()

    def repl(m):
        url = m.group(1)
        text = m.group(2)
        host = urlparse(url).netloc.lower()
        if not host or host.endswith(domain):
            return m.group(0)
        plain = re.sub(r"\s*(?:<span[^>]*>\s*)?[↗➚⧉](?:\s*</span>)?\s*", "", text)
        if is_evidence(url):
            return plain
        key = url.split("#")[0].rstrip("/")
        if key in seen:
            return plain
        seen.add(key)
        return m.group(0)
    return re.sub(r'<a\b[^>]*?href="(https?://[^"]+)"[^>]*>(.*?)</a>', repl, main, flags=re.S)


def _load_rewrites():
    import json
    f = Path(__file__).with_name("v320_rewrites.json")
    if not f.exists():
        return {}
    data = json.loads(f.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


REWRITES = _load_rewrites()


def apply_rewrites(main):
    for old, new in REWRITES.items():
        for variant in {old, old.replace("’", "&rsquo;"), old.replace("&", "&amp;")}:
            if variant in main:
                main = main.replace((" " + variant) if not new else variant, new if new else "")
                main = main.replace(variant, new)
    return main


def transform(html, domain):
    m = re.search(r"(?is)<main\b.*?</main>", html)
    if m:
        a, b = m.span()
    else:
        a = html.find("</header>")
        a = a + 9 if a >= 0 else html.lower().find("<body")
        b = html.lower().rfind("<footer")
        if a < 0 or b < 0 or b <= a:
            return html
    main = html[a:b]
    caps = []
    main = re.sub(r"<figcaption.*?</figcaption>|<script\b.*?</script>",
                  lambda x: caps.append(x.group(0)) or f"@@KEEP{len(caps)-1}@@", main, flags=re.S | re.I)
    main = drop_source_sections(main)
    main = CITE.sub("", main)
    main = CITE_A.sub("", main)
    main = TOC_SOURCES.sub("", main)
    main = NEWTAB.sub("", main)
    main = re.sub(r'\s*\((?:external(?: site| website)?, )?opens? (?:in )?a new (?:tab|window)\)', "", main)
    for pat in HEDGE:
        main = re.sub(pat, "", main)
    main = apply_rewrites(main)
    main = unwrap_links(main, domain)
    main = DANGLING.sub(lambda x: x.group(1), main)
    main = re.sub(r"<p>\s*</p>|<li>\s*</li>", "", main)
    # Table-of-contents labels left behind after their sources section was removed.
    main = re.sub(r"(?<=>)\s*Sources?\s*(?:&amp;|&)\s*(?:verification|checks|limits)\s*(?=</(?:nav|div|aside|ol|ul|li|p)>)", "", main)
    main = re.sub(r"@@KEEP(\d+)@@", lambda x: caps[int(x.group(1))], main)
    out = html[:a] + main + html[b:]
    # Unwrap in-page links whose target id disappeared with a removed section.
    ids = set(re.findall(r'\sid="([^"]+)"', out))
    body_a, body_b = a, a + len(main)
    seg = out[body_a:body_b]
    seg = re.sub(r'<a\s[^>]*href="#([^"]+)"[^>]*>(.*?)</a>',
                 lambda x: x.group(0) if x.group(1) in ids else x.group(2), seg, flags=re.S)
    return out[:body_a] + seg + out[body_b:]


def iter_pages(root):
    for f in root.rglob("*.html"):
        rel = f.relative_to(root)
        parts = rel.parts
        if any(p in SKIP_DIRS or p.startswith(".") for p in parts[:-1]) or f.name == "404.html":
            continue
        if TRUST.match(rel.as_posix()):
            continue
        yield f


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    args = [x for x in args if not x.startswith("--")]
    root = Path(args[0]).resolve()
    domain = root.name.lower().removeprefix("www.")
    files = [root / p for p in args[1:]] if args[1:] else list(iter_pages(root))
    changed = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="strict")
        if re.search(r'(?i)<meta[^>]+name="robots"[^>]+noindex', text):
            continue
        new = transform(text, domain)
        if new != text:
            changed += 1
            if not dry:
                f.write_text(new, encoding="utf-8", newline="")
    print(f"{root.name}: {changed}/{len(files)} pages {'would change' if dry else 'changed'}")


if __name__ == "__main__":
    main()
