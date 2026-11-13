#!/usr/bin/env python3
"""Notify-only site watch (SOP 05 §2.9.1). Stdlib only.

  python scripts/site_watch.py sentinel    --config config/sentinel.json         [--dry-run]
  python scripts/site_watch.py competitors --config config/competitor-watch.json [--dry-run]

Never edits the site. State lives in GitHub Issues (hidden marker block in the
newest issue per source), so the workflow only needs `issues: write`.
First run for a source records a baseline issue and closes it immediately.
Env: GITHUB_TOKEN, GITHUB_REPOSITORY (owner/repo). Without them, dry-run only.
"""
import argparse, base64, gzip, hashlib, json, os, re, sys, time
import urllib.error, urllib.parse, urllib.request, urllib.robotparser
import xml.etree.ElementTree as ET

UA = "site-watch/1.0 (+notify-only; fan site content freshness)"
API = "https://api.github.com"
BODY_LIMIT = 60000
STATE_RE = re.compile(r"<!-- site-watch-state (\S+) -->")


class WatchError(Exception):
    pass


def http_get(url, headers=None, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            if not data.strip():
                raise WatchError("empty response " + url)
            return data
        except (urllib.error.URLError, TimeoutError, WatchError) as e:
            last = e
            if isinstance(e, urllib.error.HTTPError) and e.code in (401, 403, 404):
                break
            time.sleep(5 * (i + 1))
    raise WatchError(f"fetch failed {url}: {last}")


# ---------- GitHub Issues as state + notification ----------

class Issues:
    def __init__(self, dry_run):
        self.repo = os.environ.get("GITHUB_REPOSITORY", "")
        self.token = os.environ.get("GITHUB_TOKEN", "")
        self.dry = dry_run or not (self.repo and self.token)

    def _call(self, method, path, payload=None):
        req = urllib.request.Request(
            API + path, method=method,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Authorization": "Bearer " + self.token, "User-Agent": UA,
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"null")

    def last_state(self, label, key):
        """Newest issue (open or closed) carrying this key's state block."""
        if not (self.repo and self.token):
            return None, None
        q = urllib.parse.quote(f'repo:{self.repo} label:{label} "site-watch-key {key}" in:body')
        res = self._call("GET", f"/search/issues?q={q}&sort=created&order=desc&per_page=5")
        for it in res.get("items", []):
            m = STATE_RE.search(it.get("body") or "")
            if m and f"site-watch-key {key} " in it["body"]:
                return json.loads(base64.b64decode(m.group(1))), it["html_url"]
        return None, None

    def ensure_label(self, label, color):
        if self.dry:
            return
        try:
            self._call("POST", f"/repos/{self.repo}/labels", {"name": label, "color": color})
        except urllib.error.HTTPError as e:
            if e.code != 422:  # 422 = already exists
                raise

    def create(self, title, body, label, key, state, close=False):
        blob = base64.b64encode(json.dumps(state, separators=(",", ":")).encode()).decode()
        tail = f"\n\n<!-- site-watch-key {key} -->\n<!-- site-watch-state {blob} -->\n"
        if len(body) + len(tail) > BODY_LIMIT:
            body = body[: BODY_LIMIT - len(tail) - 40] + "\n\n…（已截断）"
        body += tail
        if len(body) > 65000:
            raise WatchError(f"state for {key} too large for an issue body; narrow include/limit")
        if self.dry:
            print(f"--- DRY-RUN issue{' (closed baseline)' if close else ''}: {title}\n{body[:3000]}\n")
            return "(dry-run)"
        it = self._call("POST", f"/repos/{self.repo}/issues", {"title": title, "body": body, "labels": [label]})
        if close:
            self._call("PATCH", f"/repos/{self.repo}/issues/{it['number']}", {"state": "closed", "state_reason": "completed"})
        return it["html_url"]


def handoff(cfg, kind):
    site = cfg.get("site", "{站点}")
    return (f"\n### 处理方式\n把本 Issue 链接交给 `/{kind} {site}{' 事件' if kind == 'weihu' else ''} 材料:<本Issue链接>`；"
            "处理完在此写结果并关闭。本 Issue 只是通知，自动化不会修改页面。\n")


# ---------- version sentinel ----------

def get_path(obj, dotted):
    for part in dotted.split("."):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def keep_matching(src, rows):
    """Optional `title_match` regex drops sales/soundtrack posts; an empty match set is not a failure."""
    if src.get("title_match"):
        rows = [r for r in rows if re.search(src["title_match"], r["title"], re.I)]
    if not rows:
        return "(none)", {"ids": []}, []
    return rows[0]["id"], {"ids": [r["id"] for r in rows]}, rows


def snapshot(src):
    """Return (fingerprint, summary dict, items list) for one source."""
    t = src["type"]
    if t == "steam_news":
        url = ("https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid="
               f"{int(src['appid'])}&count={int(src.get('count', 10))}&maxlength=300"
               f"&feeds={src.get('feeds', 'steam_community_announcements')}")
        items = json.loads(http_get(url))["appnews"]["newsitems"]
        items = [i for i in items if int(i.get("appid", src["appid"])) == int(src["appid"])]
        if not items:
            raise WatchError("steam_news returned no items")
        rows = [{"id": str(i["gid"]), "title": i["title"], "url": i["url"],
                 "date": time.strftime("%Y-%m-%d", time.gmtime(i["date"]))} for i in items]
        return keep_matching(src, rows)
    if t == "json":
        data = json.loads(http_get(src["url"]))
        vals = {f: get_path(data, f) for f in src["fields"]}
        if any(v in (None, "") for v in vals.values()):
            raise WatchError(f"json field empty: {vals}")
        return json.dumps(vals, sort_keys=True), {"values": vals}, []
    if t == "rss":
        root = ET.fromstring(http_get(src["url"]))
        rows = []
        for it in root.iter():
            if it.tag.split("}")[-1] not in ("item", "entry"):
                continue
            get = lambda n: next((c for c in it if c.tag.split("}")[-1] == n), None)
            link = get("link")
            href = (link.get("href") or link.text) if link is not None else ""
            gid = get("guid") if get("guid") is not None else get("id")
            title = get("title")
            rows.append({"id": (gid.text if gid is not None else href) or "",
                         "title": (title.text if title is not None else "").strip(), "url": href or ""})
        rows = [r for r in rows if r["id"]][: int(src.get("count", 15))]
        if not rows:
            raise WatchError("rss returned no items")
        return keep_matching(src, rows)
    if t == "page_hash":
        text = http_get(src["url"]).decode("utf-8", "replace")
        if src.get("extract"):
            m = re.search(src["extract"], text, re.S)
            if not m:
                raise WatchError("extract pattern not found (page layout changed?)")
            text = m.group(1) if m.groups() else m.group(0)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < int(src.get("min_chars", 200)):
            raise WatchError(f"extracted text too short ({len(text)} chars)")
        return hashlib.sha256(text.encode()).hexdigest()[:16], {"chars": len(text), "head": text[:300]}, []
    raise WatchError("unknown source type " + t)


def run_sentinel(cfg, issues):
    label = cfg.get("label", "auto-sentinel")
    issues.ensure_label(label, "d93f0b")
    failures = []
    for src in cfg["sources"]:
        key = f"sentinel:{src['id']}"
        try:
            fp, summary, rows = snapshot(src)
            prev, prev_url = issues.last_state(label, key)
            state = {"fp": fp, "summary": summary, "at": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())}
            if prev is None:
                url = issues.create(f"[哨兵基线] {src['id']} 已记录", f"首次记录基线：`{fp}`，之后有变化才会通知。",
                                    label, key, state, close=True)
                print(f"{src['id']}: baseline {url}")
                continue
            if prev.get("fp") == fp:
                print(f"{src['id']}: unchanged")
                continue
            body = [f"**来源**：{src.get('name', src['id'])}（{src['type']}）  ", f"**检测时间**：{state['at']}  ",
                    f"**上次记录**：{prev.get('at')} {prev_url or ''}", "", "### 变化"]
            if rows:
                old = set(prev.get("summary", {}).get("ids", []))
                new_rows = [r for r in rows if r["id"] not in old] or rows[:1]
                body += [f"- {r.get('date', '')} [{r['title']}]({r['url']})" for r in new_rows]
            elif "values" in summary:
                ov = prev.get("summary", {}).get("values", {})
                body += [f"- `{k}`: `{ov.get(k)}` → `{v}`" for k, v in summary["values"].items() if ov.get(k) != v]
            else:
                body.append(f"- 页面内容指纹 `{prev['fp']}` → `{fp}`（{summary['chars']} 字符）。开头：{summary['head'][:200]}")
            body += ["", "### 可能受影响的页面"]
            body += [f"- {p}" for p in src.get("affected", [])] or ["- （配置未列出，处理时从生成源依赖查找）"]
            body += ["", "### 建议处理分类（处理时勾选）", "- [ ] 数值直接修改（生成源/data 中的字段）",
                     "- [ ] 需要人工判断（推荐、Tier、路线、机制解释）", "- [ ] 可能需要新建页面（进 01 题库评估）",
                     "- [ ] 无需改动（说明原因）", handoff(cfg, "weihu")]
            title_hint = rows[0]["title"][:60] if rows else fp
            url = issues.create(f"[哨兵] {src['id']} 有更新：{title_hint}", "\n".join(body), label, key, state)
            print(f"{src['id']}: CHANGED -> {url}")
        except Exception as e:  # one bad source must not hide others
            failures.append(f"{src['id']}: {e}")
            print(f"{src['id']}: FAILED {e}", file=sys.stderr)
    return failures


# ---------- competitor watch ----------

def sitemap_urls(url, limit, depth=0):
    root = ET.fromstring(http_get(url))
    tag = root.tag.split("}")[-1]
    out = {}
    for node in root:
        loc = next((c.text.strip() for c in node if c.tag.split("}")[-1] == "loc" and c.text), None)
        mod = next((c.text.strip() for c in node if c.tag.split("}")[-1] == "lastmod" and c.text), "")
        if not loc:
            continue
        if tag == "sitemapindex":
            if depth < 2:
                out.update(sitemap_urls(loc, limit - len(out), depth + 1))
        else:
            out[loc] = mod
        if len(out) >= limit:
            break
    return out


def allowed(url):
    p = urllib.parse.urlsplit(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.parse(http_get(f"{p.scheme}://{p.netloc}/robots.txt", tries=1).decode("utf-8", "replace").splitlines())
    except WatchError:
        return True  # no robots.txt
    return rp.can_fetch(UA, url) and rp.can_fetch("*", url)


def h4(s):
    return hashlib.sha1(s.encode()).digest()[:4]


def pack(urls):
    return base64.b64encode(b"".join(h4(u) + h4(u + "|" + m) for u, m in sorted(urls.items()))).decode()


def unpack(blob):
    raw = base64.b64decode(blob or "")
    return {raw[i:i + 4]: raw[i + 4:i + 8] for i in range(0, len(raw), 8)}


def slug_tokens(url):
    path = urllib.parse.urlsplit(url).path.strip("/").split("/")
    return {t for t in re.split(r"[-_/.]+", path[-1] if path else "") if len(t) > 2}


def run_competitors(cfg, issues):
    label = cfg.get("label", "competitor-watch")
    issues.ensure_label(label, "5319e7")
    limit = int(cfg.get("max_urls_per_site", 4000))
    own = {}
    if cfg.get("own_sitemap"):
        own = sitemap_urls(cfg["own_sitemap"], 20000)
    failures = []
    for comp in cfg["competitors"]:
        key = f"competitor:{comp['name']}"
        try:
            if not allowed(comp["sitemap"]):
                raise WatchError("robots.txt disallows the sitemap; remove this competitor")
            urls = sitemap_urls(comp["sitemap"], limit)
            if comp.get("include"):
                urls = {u: m for u, m in urls.items() if re.search(comp["include"], u)}
            if not urls:
                raise WatchError("sitemap yielded 0 URLs after filtering")
            prev, prev_url = issues.last_state(label, key)
            state = {"n": len(urls), "packed": pack(urls), "at": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())}
            if prev is None:
                url = issues.create(f"[同行基线] {comp['name']} 已记录 {len(urls)} 个 URL",
                                    "首次记录基线，之后每周对比新增/更新 URL。", label, key, state, close=True)
                print(f"{comp['name']}: baseline {url}")
                continue
            old = unpack(prev.get("packed"))
            if prev.get("n") and len(urls) < prev["n"] * 0.5:
                raise WatchError(f"URL count dropped {prev['n']} -> {len(urls)}; treating as fetch problem")
            added = [u for u in urls if h4(u) not in old]
            updated = [u for u in urls if h4(u) in old and old[h4(u)] != h4(u + "|" + urls[u])]
            if not added and not updated:
                print(f"{comp['name']}: unchanged")
                continue
            own_tok = [(u, slug_tokens(u)) for u in own]

            def cover(u):
                tok = slug_tokens(u)
                best = max(own_tok, key=lambda x: len(tok & x[1]), default=(None, set()))
                return f"相近：{best[0]}" if best[0] and len(tok & best[1]) >= max(1, len(tok) // 2) else "**未找到相近URL**"

            body = [f"**同行**：{comp['name']}  ", f"**对比**：{prev.get('at')} → {state['at']}（{prev_url or ''}）", "",
                    f"### 新增 URL（{len(added)}）"]
            body += [f"- {u} — {cover(u)}" for u in sorted(added)[:150]]
            body += ["", f"### lastmod 有变化（{len(updated)}，只列前 50）"]
            body += [f"- {u}" for u in sorted(updated)[:50]]
            body += ["", "> 同行有页面不等于玩家有需求；只作为选题线索，按 01 题库与第 3 步评估，不复制内容。",
                     handoff(cfg, "buquan")]
            url = issues.create(f"[同行] {comp['name']}：新增 {len(added)} / 更新 {len(updated)}",
                                "\n".join(body), label, key, state)
            print(f"{comp['name']}: CHANGED -> {url}")
        except Exception as e:
            failures.append(f"{comp['name']}: {e}")
            print(f"{comp['name']}: FAILED {e}", file=sys.stderr)
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sentinel", "competitors"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    with open(a.config, encoding="utf-8") as f:
        cfg = json.load(f)
    issues = Issues(a.dry_run)
    failures = (run_sentinel if a.mode == "sentinel" else run_competitors)(cfg, issues)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(("Failures:\n- " + "\n- ".join(failures)) if failures else "All sources checked.\n")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
