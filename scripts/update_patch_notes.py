#!/usr/bin/env python3
"""Safely update the Megabonk patch-notes hub from official Steam announcements."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

APP_ID = 3405340
API_URL = (
    "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    "?appid=3405340&count=30&maxlength=0&feeds=steam_community_announcements"
)
VERSION_RE = re.compile(r"(?i)(?:\bversion\s*|\bv)?(\d+\.\d+\.\d+)\b")
EDIT_DATE_RE = re.compile(r"(?i)\bedit\s+(\d{1,2}/\d{1,2}/\d{4})\b")
LATEST_START = "<!-- PATCH_AUTO_LATEST_START -->"
LATEST_END = "<!-- PATCH_AUTO_LATEST_END -->"
DIRECTORY_START = "<!-- PATCH_AUTO_DIRECTORY_START -->"
DIRECTORY_END = "<!-- PATCH_AUTO_DIRECTORY_END -->"
SECTIONS_START = "<!-- PATCH_AUTO_SECTIONS_START -->"
SECTIONS_END = "<!-- PATCH_AUTO_SECTIONS_END -->"


class UpdateError(RuntimeError):
    pass


class _TextExtractor(HTMLParser):
    BLOCK_TAGS = {"br", "li", "p", "div", "h1", "h2", "h3", "h4", "h5"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


@dataclass(frozen=True)
class PatchRecord:
    version: str
    release_date: str
    title: str
    bullets: tuple[str, ...]
    source_gid: str
    source_url: str
    source_hash: str


def version_key(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split("."))
    if len(parts) != 3:
        raise UpdateError(f"Unsupported version format: {value}")
    return parts


def version_slug(value: str) -> str:
    return "v" + value.replace(".", "")


def display_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def _truncate(value: str, limit: int = 240) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    shortened = value[: limit - 1].rsplit(" ", 1)[0]
    return shortened.rstrip(" ,;:-") + "…"


def markup_to_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"(?is)\[img\].*?\[/img\]", " ", value)
    value = re.sub(r"(?is)\[url=[^\]]+\](.*?)\[/url\]", r"\1", value)
    value = re.sub(r"(?is)\[/?(?:b|i|u|h\d|quote|code|list|olist|table|tr|td)[^\]]*\]", "\n", value)
    value = re.sub(r"(?is)\[/?[^\]]+\]", " ", value)
    parser = _TextExtractor()
    parser.feed(value)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_bullets(segment: str, limit: int = 12) -> tuple[str, ...]:
    candidates: list[str] = []
    candidates.extend(re.findall(r"(?is)<li\b[^>]*>(.*?)</li>", segment))
    candidates.extend(re.findall(r"(?is)\[\*\](.*?)(?=\[\*\]|\[/list\])", segment))

    cleaned: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        value = _truncate(markup_to_text(candidate))
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            cleaned.append(value)
        if len(cleaned) >= limit:
            return tuple(cleaned)

    if cleaned:
        return tuple(cleaned)

    ignored = {
        "bugs", "bug fixes", "other", "game", "balancing", "balance",
        "new stuff", "ui", "system", "settings", "changelog", "tldr",
    }
    for line in markup_to_text(segment).splitlines():
        value = _truncate(line.lstrip("-•* ").strip())
        if (
            len(value) < 18
            or value.casefold() in ignored
            or VERSION_RE.fullmatch(value)
            or value.casefold().startswith("edit ")
        ):
            continue
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            cleaned.append(value)
        if len(cleaned) >= min(limit, 6):
            break
    return tuple(cleaned)


def _official_news_item(item: dict[str, Any]) -> bool:
    try:
        if "appid" in item and int(item["appid"]) != APP_ID:
            return False
    except (TypeError, ValueError):
        return False

    feedname = str(item.get("feedname", "")).casefold()
    if feedname and feedname != "steam_community_announcements":
        return False

    parsed = urlparse(str(item.get("url", "")))
    allowed_host = parsed.hostname in {
        "store.steampowered.com",
        "steamcommunity.com",
        "www.steamcommunity.com",
    }
    official_cdn_post = (
        parsed.hostname == "steamstore-a.akamaihd.net"
        and "/news/externalpost/steam_community_announcements/" in parsed.path
    )
    return (
        (allowed_host and str(APP_ID) in parsed.path)
        or official_cdn_post
    )


def _item_hash(item: dict[str, Any]) -> str:
    stable = {
        "gid": str(item.get("gid", "")),
        "title": str(item.get("title", "")),
        "contents": str(item.get("contents", "")),
        "date": int(item.get("date", 0) or 0),
        "url": str(item.get("url", "")),
    }
    encoded = json.dumps(stable, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _date_for_match(combined: str, position: int, published: date) -> date:
    lookback = combined[max(0, position - 180) : position]
    edits = list(EDIT_DATE_RE.finditer(lookback))
    if not edits:
        return published
    try:
        return datetime.strptime(edits[-1].group(1), "%m/%d/%Y").date()
    except ValueError:
        return published


def parse_official_news(payload: dict[str, Any]) -> list[PatchRecord]:
    newsitems = payload.get("appnews", {}).get("newsitems", [])
    if not isinstance(newsitems, list):
        raise UpdateError("Steam response did not contain appnews.newsitems")

    official_items = [item for item in newsitems if isinstance(item, dict) and _official_news_item(item)]
    if not official_items:
        raise UpdateError("Steam response contained no official Megabonk announcements")

    records: dict[str, PatchRecord] = {}
    for item in official_items:
        title = str(item.get("title", "")).strip()
        contents = str(item.get("contents", ""))
        combined = title + "\n" + contents
        matches = list(VERSION_RE.finditer(combined))
        if not matches:
            continue

        published = datetime.fromtimestamp(
            int(item.get("date", 0) or 0), tz=timezone.utc
        ).date()
        source_hash = _item_hash(item)
        source_gid = str(item.get("gid", ""))
        source_url = str(item.get("url", ""))

        for index, match in enumerate(matches):
            version = match.group(1)
            if version_key(version) < (1, 0, 0):
                continue

            context = combined[max(0, match.start() - 70) : match.end() + 70]
            in_title = bool(VERSION_RE.search(title) and version in title)
            labeled = bool(
                re.search(
                    rf"(?is)(?:patch|hotfix|update|version).{{0,70}}v?{re.escape(version)}"
                    rf"|v?{re.escape(version)}.{{0,40}}(?:patch|hotfix|update)",
                    context,
                )
            )
            if not (in_title or labeled):
                continue

            next_position = len(combined)
            for later in matches[index + 1 :]:
                if later.group(1) != version:
                    next_position = later.start()
                    break
            segment = combined[match.start() : next_position]
            bullets = extract_bullets(segment)
            if not bullets:
                continue

            patch_date = _date_for_match(combined, match.start(), published)
            record = PatchRecord(
                version=version,
                release_date=patch_date.isoformat(),
                title=title or f"Megabonk V{version}",
                bullets=bullets,
                source_gid=source_gid,
                source_url=source_url,
                source_hash=source_hash,
            )
            existing = records.get(version)
            if existing is None or record.release_date >= existing.release_date:
                records[version] = record

    return sorted(records.values(), key=lambda record: version_key(record.version))


def fetch_news(retries: int = 3) -> dict[str, Any]:
    request = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "Megabonk.org Patch Notes Updater/1.0",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise UpdateError(f"Unable to fetch Steam News API after {retries} attempts: {last_error}")


def _replace_once(text: str, pattern: str, replacement: str, label: str, flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise UpdateError(f"Could not update {label}; expected one match, found {count}")
    return updated


def _replace_marker_block(text: str, start: str, end: str, body: str, label: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise UpdateError(f"Invalid {label} markers")
    pattern = re.escape(start) + r".*?" + re.escape(end)
    replacement = start + "\n" + body.rstrip() + "\n    " + end
    return _replace_once(text, pattern, replacement, label, flags=re.DOTALL)


def _marker_body(text: str, start: str, end: str, label: str) -> str:
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)
    if not match:
        raise UpdateError(f"Missing {label} markers")
    return match.group(1).strip("\r\n")


def render_card(record: PatchRecord, latest: bool) -> str:
    badge = '\n                    <span class="version-tag">Latest</span>' if latest else ""
    return (
        f'                <a href="#{version_slug(record.version)}" class="version-card'
        f'{" latest" if latest else " hotfix"}" data-patch-version="{html.escape(record.version)}">\n'
        f'                    <span class="version-number">V{html.escape(record.version)}</span>\n'
        f'                    <span class="version-date">{html.escape(display_date(record.release_date))}</span>'
        f'{badge}\n'
        f'                </a>'
    )


def render_section(record: PatchRecord, latest: bool) -> str:
    slug = version_slug(record.version)
    badge = '\n                            <span class="patch-badge latest">Latest</span>' if latest else ""
    bullets = "\n".join(
        f"                                <li>{html.escape(item)}</li>"
        for item in record.bullets[:12]
    )
    return f"""                <!-- PATCH_AUTO_VERSION_{slug}_START -->
                <section id="{slug}" class="patch-section{' latest-patch' if latest else ''}" data-patch-version="{html.escape(record.version)}">
                    <div class="patch-header">
                        <div class="patch-title-group">
                            <h2>Version {html.escape(record.version)} Patch Notes</h2>{badge}
                        </div>
                        <div class="patch-meta">
                            <span class="patch-date">📅 {html.escape(display_date(record.release_date))}</span>
                            <span class="patch-name">🛠️ Official Patch &amp; Hotfix Changes</span>
                        </div>
                    </div>
                    <div class="patch-content">
                        <div class="patch-summary">
                            <h3>What Changed</h3>
                            <ul>
{bullets}
                            </ul>
                        </div>
                        <p><strong>Player note:</strong> Restart Steam and confirm the game has updated before checking these changes in a run.</p>
                    </div>
                </section>
                <!-- PATCH_AUTO_VERSION_{slug}_END -->"""


def render_latest_summary(record: PatchRecord) -> str:
    bullets = "\n".join(
        f"                    <li>{html.escape(item)}</li>" for item in record.bullets[:6]
    )
    return f"""    <section class="latest-summary" id="latest-patch-summary" aria-labelledby="latest-patch-title">
        <div class="container">
            <div class="latest-summary-card">
                <h2 id="latest-patch-title">Latest Patch Summary</h2>
                <p class="latest-version-line"><strong>V{html.escape(record.version)}</strong> · Released {html.escape(display_date(record.release_date))}</p>
                <p>This is the newest version found in Megabonk's official Steam announcements.</p>
                <ul class="summary-grid">
{bullets}
                </ul>
                <div class="summary-actions">
                    <a class="btn-primary" href="#{version_slug(record.version)}">Read V{html.escape(record.version)} Details ↓</a>
                </div>
            </div>
        </div>
    </section>"""


def update_page(page: str, records: list[PatchRecord], today: date) -> tuple[str, str]:
    for marker in (
        LATEST_START, LATEST_END, DIRECTORY_START, DIRECTORY_END,
        SECTIONS_START, SECTIONS_END,
    ):
        if page.count(marker) != 1:
            raise UpdateError(f"Patch page is missing unique marker: {marker}")

    version_match = re.search(r'<meta name="patch-version" content="(\d+\.\d+\.\d+)">', page)
    if not version_match:
        raise UpdateError("Patch page is missing the patch-version meta tag")
    current_version = version_match.group(1)
    latest_record = max(records, key=lambda record: version_key(record.version))
    target_version = max(current_version, latest_record.version, key=version_key)
    if target_version != latest_record.version:
        raise UpdateError(
            f"Steam latest V{latest_record.version} is older than page V{current_version}; refusing downgrade"
        )

    directory = _marker_body(page, DIRECTORY_START, DIRECTORY_END, "directory")
    directory = re.sub(r'\s*<span class="version-tag">Latest</span>', "", directory)
    directory = directory.replace(" version-card latest", " version-card")
    sections = _marker_body(page, SECTIONS_START, SECTIONS_END, "sections")
    sections = sections.replace(" patch-section latest-patch", " patch-section")
    sections = re.sub(r'\s*<span class="patch-badge latest">Latest</span>', "", sections)

    for record in sorted(records, key=lambda item: version_key(item.version)):
        card_pattern = (
            rf'<a\b[^>]*data-patch-version="{re.escape(record.version)}"[^>]*>.*?</a>'
        )
        card = render_card(record, latest=record.version == target_version)
        if re.search(card_pattern, directory, re.DOTALL):
            directory = re.sub(card_pattern, card, directory, count=1, flags=re.DOTALL)
        elif version_key(record.version) > version_key(current_version):
            directory = card + "\n" + directory

        slug = version_slug(record.version)
        section_pattern = (
            re.escape(f"<!-- PATCH_AUTO_VERSION_{slug}_START -->")
            + r".*?"
            + re.escape(f"<!-- PATCH_AUTO_VERSION_{slug}_END -->")
        )
        section = render_section(record, latest=record.version == target_version)
        if re.search(section_pattern, sections, re.DOTALL):
            sections = re.sub(section_pattern, section, sections, count=1, flags=re.DOTALL)
        elif version_key(record.version) > version_key(current_version):
            sections = section + "\n\n" + sections

    latest = next(record for record in records if record.version == target_version)
    page = _replace_marker_block(
        page, LATEST_START, LATEST_END, render_latest_summary(latest), "latest summary"
    )
    page = _replace_marker_block(page, DIRECTORY_START, DIRECTORY_END, directory, "directory")
    page = _replace_marker_block(page, SECTIONS_START, SECTIONS_END, sections, "sections")

    version_label = f"V{target_version}"
    date_label = display_date(latest.release_date)
    description = (
        f"Megabonk {version_label} patch notes for {date_label}, with the latest update "
        "summary, fixes and a stable version directory."
    )
    social_description = (
        f"Latest Megabonk {version_label} patch summary and version-by-version update archive."
    )
    title = f"Megabonk Patch Notes {version_label} – {date_label}"

    page = _replace_once(page, r"<title>.*?</title>", f"<title>{title}</title>", "title", re.DOTALL)
    page = _replace_once(
        page,
        r'(<meta name="description"\s+content=")[^"]*(">)',
        rf"\g<1>{description}\2",
        "meta description",
        re.DOTALL,
    )
    page = _replace_once(
        page, r'<meta name="patch-version" content="[^"]+">',
        f'<meta name="patch-version" content="{target_version}">', "patch version meta"
    )
    page = _replace_once(
        page, r'<meta property="og:title" content="[^"]+">',
        f'<meta property="og:title" content="{title}">', "og title"
    )
    page = _replace_once(
        page, r'<meta property="og:description"\s+content="[^"]+">',
        f'<meta property="og:description" content="{social_description}">', "og description"
    )
    page = _replace_once(
        page, r'<meta name="twitter:title" content="[^"]+">',
        f'<meta name="twitter:title" content="{title}">', "twitter title"
    )
    page = _replace_once(
        page, r'<meta name="twitter:description"\s+content="[^"]+">',
        f'<meta name="twitter:description" content="{social_description}">', "twitter description"
    )
    page = _replace_once(
        page, r'("headline":\s*)"[^"]+"',
        rf'\g<1>"{title}"', "article headline"
    )
    page = _replace_once(
        page, r'("dateModified":\s*)"\d{4}-\d{2}-\d{2}"',
        rf'\g<1>"{today.isoformat()}"', "dateModified"
    )
    faq_answer = (
        f"The latest officially documented patch is {version_label}, dated {date_label}. "
        "See the Latest Patch Summary for the main changes."
    )
    page = _replace_once(
        page,
        r'("name":\s*"What is the latest Megabonk patch version\?".*?"text":\s*")[^"]*(")',
        rf"\g<1>{faq_answer}\2",
        "latest patch FAQ",
        re.DOTALL,
    )
    page = _replace_once(
        page, r"<h1>Megabonk Patch Notes V[^<]+</h1>",
        f"<h1>Megabonk Patch Notes {version_label}</h1>", "H1"
    )
    page = _replace_once(
        page, r'<span class="meta-item">📅 Latest Patch: [^<]+</span>',
        f'<span class="meta-item">📅 Latest Patch: {date_label}</span>', "hero patch date"
    )
    page = _replace_once(
        page, r'<span class="meta-item">🎮 Game Version: V[^<]+</span>',
        f'<span class="meta-item">🎮 Game Version: {version_label}</span>', "hero version"
    )
    return page, target_version


def update_sitemap(sitemap: str, today: date) -> str:
    pattern = (
        r"(<loc>https://megabonk\.org/guides/patch-notes/</loc>\s*"
        r"<lastmod>)\d{4}-\d{2}-\d{2}(</lastmod>)"
    )
    return _replace_once(
        sitemap, pattern, rf"\g<1>{today.isoformat()}\2", "sitemap lastmod", re.DOTALL
    )


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "appid": APP_ID, "latest_version": "0.0.0", "versions": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if int(state.get("appid", 0)) != APP_ID:
        raise UpdateError("Patch state has the wrong Steam appid")
    return state


def write_json_if_changed(path: Path, value: dict[str, Any]) -> bool:
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == rendered:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8", newline="\n")
    return True


def run_update(
    payload: dict[str, Any],
    page_path: Path,
    sitemap_path: Path,
    state_path: Path,
    today: date,
) -> dict[str, Any]:
    records = parse_official_news(payload)
    if not records:
        raise UpdateError("No versioned official patch announcements were found")

    state = load_state(state_path)
    page = page_path.read_text(encoding="utf-8")
    sitemap = sitemap_path.read_text(encoding="utf-8")
    current_match = re.search(r'<meta name="patch-version" content="(\d+\.\d+\.\d+)">', page)
    if not current_match:
        raise UpdateError("Patch page is missing patch-version metadata")
    current_version = current_match.group(1)

    previous_versions = state.get("versions", {})
    discovered = {record.version: record for record in records}
    new_records = [
        record for record in records
        if version_key(record.version) > version_key(current_version)
    ]

    latest_api = max(records, key=lambda record: version_key(record.version))
    previous_latest = previous_versions.get(current_version, {})
    latest_was_edited = (
        latest_api.version == current_version
        and bool(previous_latest.get("source_hash"))
        and previous_latest.get("source_hash") != latest_api.source_hash
    )

    page_records: list[PatchRecord] = []
    if new_records:
        page_records = [
            record for record in records
            if version_key(record.version) >= version_key(current_version)
        ]
    elif latest_was_edited:
        page_records = [latest_api]

    page_changed = False
    if page_records:
        updated_page, target_version = update_page(page, page_records, today)
        updated_sitemap = update_sitemap(sitemap, today)
        if updated_page != page:
            page_path.write_text(updated_page, encoding="utf-8", newline="\n")
            page_changed = True
        if updated_sitemap != sitemap:
            sitemap_path.write_text(updated_sitemap, encoding="utf-8", newline="\n")
        current_version = target_version

    versions = dict(previous_versions)
    for record in records:
        versions[record.version] = {
            **asdict(record),
            "bullets": list(record.bullets),
        }
    state.update(
        {
            "schema_version": 1,
            "appid": APP_ID,
            "api_url": API_URL,
            "latest_version": max(
                [current_version, *discovered.keys()], key=version_key
            ),
            "versions": versions,
        }
    )
    state_changed = write_json_if_changed(state_path, state)
    return {
        "page_changed": page_changed,
        "state_changed": state_changed,
        "latest_version": state["latest_version"],
        "new_versions": [record.version for record in new_records],
        "latest_edited": latest_was_edited,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Read Steam API JSON from a fixture")
    parser.add_argument("--page", type=Path, default=Path("guides/patch-notes/index.html"))
    parser.add_argument("--sitemap", type=Path, default=Path("sitemap.xml"))
    parser.add_argument("--state", type=Path, default=Path("data/patch-notes-state.json"))
    parser.add_argument("--today", help="Override today's date (YYYY-MM-DD) for tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = (
            json.loads(args.input.read_text(encoding="utf-8"))
            if args.input
            else fetch_news()
        )
        today = date.fromisoformat(args.today) if args.today else datetime.now(timezone.utc).date()
        result = run_update(payload, args.page, args.sitemap, args.state, today)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (UpdateError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Patch updater failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
