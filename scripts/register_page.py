#!/usr/bin/env python3
"""Sync a game section's structure from its page manifest (SOP v3.24, 02 §2.6).

Usage:
  python register_page.py PROJECT_DIR GAME            apply: rewrite nav / breadcrumbs / related, sync registries
  python register_page.py PROJECT_DIR GAME --check    report differences only (exit 1 if any)

Manifest: PROJECT_DIR/data/GAME-pages.json (see 模板/pages.example.json). Rows with "plain": true
(trust pages, other-language pages) get the nav only, no breadcrumbs or related list.
Applied to every page listed (idempotent; run as the LAST build step or after manual edits):
  - desktop + mobile nav    <nav class="desktop-nav"> / <nav class="mobile-links"> get the manifest nav (current page marked)
  - breadcrumbs             <nav class="crumbs" data-reg> before the article head + BreadcrumbList JSON-LD (inner pages)
  - related tasks           <section class="related-tasks" data-reg> before "Back to top" (inner pages)
  - footer (v3.25)          when the manifest has a "footer" block: the page's last <footer> becomes
                            <footer class="site-footer" data-reg> (brand, section columns from rows with
                            "footer": true, recently updated, official links, info row) — all pages incl. plain
Registries synced (only entries for this game's pages are added; nothing else is removed):
  sitemap.xml <url>, data/content-dates.json, data/game-seo.json "pages", config/integrations.json includes.
Checks: footer link count (15–25) and footer links back to the main site other than the info row,
orphan pages (fewer than 2 inbound links from other pages of the section), pages in the folder
missing from the manifest, manifest rows without a file.
"""
import html
import json
import re
import sys
from pathlib import Path


def load(root, game):
    m = json.loads((root / "data" / f"{game}-pages.json").read_text(encoding="utf-8"))
    m["by"] = {p["slug"]: p for p in m["pages"]}
    return m


def url(m, slug):
    return m["base"] + (slug + "/" if slug else "")


def file_of(root, m, slug):
    return root / m["base"].strip("/") / (slug + "/" if slug else "") / "index.html"


def nav_html(m, slug):
    out = []
    for s in m["nav"]:
        p = m["by"][s]
        cur = ' aria-current="page"' if s == slug else ""
        label = next((x["label"] for x in m["sections"] if x["id"] == p.get("section")), p["title"])
        out.append(f'<a href="{url(m, s)}"{cur}>{html.escape(label)}</a>')
    out += [f'<a href="{x["href"]}">{html.escape(x["label"])}</a>' for x in m.get("nav_extra", [])]
    return "".join(out)


def crumbs_html(m, slug):
    p = m["by"][slug]
    items = [(m["name"], url(m, ""))]
    sec = p.get("section")
    owner = next((s for s in m["nav"] if m["by"][s].get("section") == sec), None)
    if sec and owner and owner != slug:
        label = next(x["label"] for x in m["sections"] if x["id"] == sec)
        items.append((label, url(m, owner)))
    items.append((p["title"], None))
    vis = '<nav class="crumbs" data-reg aria-label="Breadcrumb">' + " <span aria-hidden=\"true\">›</span> ".join(
        f'<a href="{u}">{html.escape(n)}</a>' if u else f'<span aria-current="page">{html.escape(n)}</span>' for n, u in items) + "</nav>"
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": m["site"] + (u or url(m, slug))})} for i, (n, u) in enumerate(items)]}
    return vis, '<script type="application/ld+json" data-reg="crumbs">' + json.dumps(ld, ensure_ascii=False) + "</script>"


def related_html(m, slug):
    p = m["by"][slug]
    picks = []
    same = [q["slug"] for q in m["pages"] if q["slug"] not in ("", slug) and q.get("section") == p.get("section")]
    for s in same[:2] + p.get("related", []):
        if s in m["by"] and s not in picks and s != slug:
            picks.append(s)
    picks = picks[:4]
    links = "".join(f'<a href="{url(m, s)}">{html.escape(m["by"][s]["title"])} <span aria-hidden="true">→</span></a>' for s in picks)
    links += f'<a href="{url(m, "")}">{html.escape(m["name"])} guide home <span aria-hidden="true">→</span></a>'
    return f'<section class="related-tasks" data-reg aria-label="Related guides"><h2>Related guides</h2><div class="related-links">{links}</div></section>'


def footer_html(m):
    f = m["footer"]
    e = html.escape
    cols = []
    # columns: footer.columns groups several sections under one heading; default is one column per section
    groups = f.get("columns") or [{"label": x["label"], "sections": [x["id"]]} for x in m["sections"]]
    for g in groups:
        rows = [p for sid in g["sections"] for p in m["pages"] if p.get("footer") and p.get("section") == sid][:6]
        if rows:
            cols.append(f'<div class="footer-col"><h2>{e(g["label"])}</h2>' + "".join(f'<a href="{url(m, p["slug"])}">{e(p["title"])}</a>' for p in rows) + "</div>")
    recent = sorted((p for p in m["pages"] if p["slug"] and not p.get("plain") and p.get("updated")), key=lambda p: p["updated"], reverse=True)[:3]
    if recent:
        ver = f'<p class="footer-version">{e(f["version"])}</p>' if f.get("version") else ""
        cols.append('<div class="footer-col"><h2>Recently updated</h2>' + "".join(f'<a href="{url(m, p["slug"])}">{e(p["title"])}</a>' for p in recent) + ver + "</div>")
    if f.get("official"):
        cols.append('<div class="footer-col"><h2>Official links</h2>' + "".join(f'<a href="{x["href"]}" rel="noopener">{e(x["label"])}</a>' for x in f["official"][:3]) + "</div>")
    brand = f'<div class="footer-brand"><a href="{url(m, "")}"><strong>{e(f.get("name", m["name"]))}</strong></a><p>{e(f.get("tagline", ""))}</p><p>{e(f.get("disclaimer", ""))}</p></div>'
    info = "".join(f'<a href="{x["href"]}">{e(x["label"])}</a>' for x in f.get("info", []))
    return (f'<footer class="site-footer" data-reg><div class="wrap footer-grid">{brand}{"".join(cols)}</div>'
            f'<nav class="footer-info" aria-label="Site information"><div class="wrap">{info}</div></nav></footer>')


def footer_problems(m):
    if "footer" not in m:
        return []
    out = []
    links = re.findall(r'href="([^"]+)"', footer_html(m))
    if not 15 <= len(links) <= 25:
        out.append(f"footer has {len(links)} links (aim for 15-25)")
    allowed = {x["href"] for x in m["footer"].get("info", [])} | {x["href"] for x in m["footer"].get("official", [])}
    for h in links:
        if h.startswith("/") and not h.startswith(m["base"]) and h not in allowed:
            out.append(f"footer links out of the section: {h}")
    return out


def apply_page(text, m, slug):
    nav = nav_html(m, slug)
    text = re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)', lambda x: x[1] + nav + x[2], text, flags=re.S)
    text = re.sub(r'<nav class="crumbs" data-reg[^>]*>.*?</nav>', "", text, flags=re.S)
    want_ld = crumbs_html(m, slug)[1] if slug and not m["by"][slug].get("plain") else None
    if not (want_ld and want_ld in text):
        # an unchanged BreadcrumbList stays where it is, so later SEO editors that append to <head> stay idempotent
        text = re.sub(r'<script type="application/ld\+json" data-reg="crumbs">.*?</script>', "", text, flags=re.S)
    text = re.sub(r'<section class="related-tasks" data-reg[^>]*>.*?</section>', "", text, flags=re.S)
    if "footer" in m:
        foot = footer_html(m)
        ends = [x for x in re.finditer(r"<footer\b[^>]*>.*?</footer>", text, flags=re.S)]
        if ends:
            last = ends[-1]
            text = text[:last.start()] + foot + text[last.end():]
        else:
            text = text.replace("</body>", foot + "</body>", 1)
    if slug and not m["by"][slug].get("plain"):
        vis, ld = crumbs_html(m, slug)
        text = re.sub(r'(<header class="article-head"[^>]*>)', lambda x: vis + x[1], text, count=1)
        if ld not in text:
            text = text.replace("</head>", ld + "</head>", 1)
        rel = related_html(m, slug)
        if '<p><a href="#guide">Back to top' in text:
            text = text.replace('<p><a href="#guide">Back to top', rel + '<p><a href="#guide">Back to top', 1)
        else:
            text = text.replace("</article>", rel + "</article>", 1)
    return text


def sync_registries(root, m, check):
    diffs = []
    pages = [p for p in m["pages"] if file_of(root, m, p["slug"]).exists()]
    rels = [file_of(root, m, p["slug"]).relative_to(root).as_posix() for p in pages]
    # sitemap
    sp = root / "sitemap.xml"
    if sp.exists():
        t = sp.read_text(encoding="utf-8")
        for p in pages:
            loc = m["site"] + url(m, p["slug"])
            if f"<loc>{loc}</loc>" not in t:
                diffs.append(f"sitemap missing {loc}")
                if not check:
                    entry = f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{p.get('updated', '')}</lastmod>\n    <changefreq>weekly</changefreq>\n  </url>\n"
                    t = t.replace("</urlset>", entry + "</urlset>", 1)
        if not check:
            sp.write_text(t, encoding="utf-8")
    # content dates
    cp = root / "data" / "content-dates.json"
    if cp.exists():
        d = json.loads(cp.read_text(encoding="utf-8"))
        for p in pages:
            k = m["site"] + url(m, p["slug"])
            if k not in d and p.get("updated"):
                diffs.append(f"content-dates missing {k}")
                d[k] = p["updated"]
        if not check:
            cp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # SEO registry
    gp = root / "data" / "game-seo.json"
    if gp.exists():
        d = json.loads(gp.read_text(encoding="utf-8"))
        for r in rels:
            if r not in d.get("pages", {}):
                diffs.append(f"game-seo missing {r}")
                d.setdefault("pages", {})[r] = {"questions": [], "reviewed_candidates": [], "faq_review": "Registered by register_page.py; review visible FAQ.", "language_review": "No equivalent translated page."}
        if not check:
            gp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # integrations
    ip = root / "config" / "integrations.json"
    if ip.exists() and m.get("integrations"):
        d = json.loads(ip.read_text(encoding="utf-8"))
        # trust pages ("plain") never get page integrations such as ads (00 §2)
        ordinary = [file_of(root, m, p["slug"]).relative_to(root).as_posix() for p in pages if not p.get("plain")]
        want = {i: list(ordinary) for i in m["integrations"].get("all", [])}
        vid = m["integrations"].get("video")
        if vid:
            want.setdefault(vid, []).extend(file_of(root, m, p["slug"]).relative_to(root).as_posix() for p in pages if p.get("video"))
        for i in d["integrations"]:
            for r in want.get(i["id"], []):
                if r not in i["include"]:
                    diffs.append(f"integration {i['id']} missing {r}")
                    i["include"].append(r)
        if not check:
            ip.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return diffs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    root, game = Path(args[0]).resolve(), args[1]
    m = load(root, game)
    diffs = []
    folder = root / m["base"].strip("/")
    listed = {file_of(root, m, p["slug"]).resolve() for p in m["pages"]}
    for f in folder.rglob("index.html"):
        if f.resolve() not in listed and not any(x in f.parts for x in ("_private",)):
            diffs.append(f"page not in manifest: {f.relative_to(root).as_posix()}")
    for p in m["pages"]:
        f = file_of(root, m, p["slug"])
        if not f.exists():
            diffs.append(f"manifest row without file: {p['slug']}")
            continue
        old = f.read_text(encoding="utf-8")
        new = apply_page(old, m, p["slug"])
        if new != old:
            diffs.append(f"structure out of date: {f.relative_to(root).as_posix()}")
            if not check:
                f.write_text(new, encoding="utf-8")
    diffs += sync_registries(root, m, check)
    diffs += ["footer: " + x for x in footer_problems(m)]
    # orphans: inbound links from other section pages
    texts = {p["slug"]: file_of(root, m, p["slug"]).read_text(encoding="utf-8") for p in m["pages"] if file_of(root, m, p["slug"]).exists()}
    for s in texts:
        if not s or m["by"][s].get("plain"):
            continue
        n = sum(1 for o, t in texts.items() if o != s and f'href="{url(m, s)}' in t)
        if n < 2:
            diffs.append(f"orphan risk: {url(m, s)} has {n} inbound links from the section")
    warn = ("orphan", "page not", "manifest row", "footer:")
    for d in diffs:
        print(("WARN  " if d.startswith(warn) else "DIFF  " if check else "FIXED ") + d)
    hard = [d for d in diffs if d.startswith(warn)]
    print(f"{len(m['pages'])} pages in manifest; {len(diffs) - len(hard)} {'differences' if check else 'updates'}; {len(hard)} warnings")
    sys.exit(1 if (check and diffs) or hard else 0)


if __name__ == "__main__":
    main()
