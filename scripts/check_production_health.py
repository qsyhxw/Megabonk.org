#!/usr/bin/env python3
"""Verify production data feeds and rendered character Build signals."""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://megabonk.org"
NON_CANONICAL_BUILD_PAGES = {
    "gigachad-best-build/index.html",
    "knight-best-build/index.html",
    "skeleton-best-build/index.html",
    "zorro-best-build/index.html",
}


def canonical_build_paths() -> list[str]:
    builds = ROOT / "guides" / "builds"
    pages = [*builds.glob("*-best-build.html"), *builds.glob("*-best-build/index.html")]
    selected = sorted(
        page
        for page in pages
        if page.relative_to(builds).as_posix() not in NON_CANONICAL_BUILD_PAGES
    )
    paths = []
    for page in selected:
        relative = page.relative_to(ROOT).as_posix()
        if relative.endswith("/index.html"):
            relative = relative.removesuffix("index.html")
        else:
            relative = relative.removesuffix(".html")
        paths.append("/" + relative)
    return paths


def fetch_json(base_url: str, path: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(3):
        request = urllib.request.Request(
            base_url.rstrip("/") + path,
            headers={"User-Agent": "Megabonk.org production health monitor"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError(f"{path} returned HTTP {response.status}")
                return json.load(response)
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed after 3 attempts: {last_error}")


def validate_feeds(base_url: str) -> list[str]:
    errors: list[str] = []
    checks = (
        ("/leaderboard-data.json", "data", 100),
        ("/data/leaderboard-meta.json", "characters", 1),
        ("/data/character-build-signals.json", "characterSignals", 21),
    )
    for path, field, minimum in checks:
        try:
            payload = fetch_json(base_url, path)
            records = payload.get(field)
            if not isinstance(records, list) or len(records) < minimum:
                count = len(records) if isinstance(records, list) else "invalid"
                errors.append(f"{path}: expected at least {minimum} {field}, got {count}")
        except Exception as error:
            errors.append(f"{path}: {error}")

    try:
        player_count = fetch_json(base_url, "/data/player-count.json")
        official = player_count.get("official", {})
        charts = player_count.get("steamCharts", {})
        if int(official.get("currentPlayers", 0)) <= 0:
            errors.append("/data/player-count.json: currentPlayers is empty")
        if int(charts.get("peak24h", 0)) <= 0 or int(charts.get("allTimePeak", 0)) <= 0:
            errors.append("/data/player-count.json: peak values are empty")
    except Exception as error:
        errors.append(f"/data/player-count.json: {error}")

    try:
        patch = fetch_json(base_url, "/data/patch-notes-state.json")
        if not str(patch.get("latest_version", "")).strip():
            errors.append("/data/patch-notes-state.json: latest_version is empty")
    except Exception as error:
        errors.append(f"/data/patch-notes-state.json: {error}")
    return errors


def validate_rendered_builds(base_url: str, paths: list[str]) -> list[str]:
    from playwright.sync_api import sync_playwright

    errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Megabonk.org production health monitor")
        page = context.new_page()
        for path in paths:
            try:
                response = page.goto(
                    base_url.rstrip("/") + path,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )
                if not response or not response.ok:
                    status = response.status if response else "no response"
                    raise RuntimeError(f"HTTP {status}")
                container = page.locator("[data-character-build-signals]")
                container.wait_for(state="visible", timeout=15_000)
                page.locator("[data-character-build-signals] .cbs-title").wait_for(
                    state="visible", timeout=20_000
                )
                text = container.inner_text(timeout=5_000)
                if "temporarily unavailable" in text.lower():
                    raise RuntimeError("rendered the unavailable fallback")
                if "Leaderboard Builds" not in text:
                    raise RuntimeError("leaderboard Build heading was not rendered")
            except Exception as error:
                errors.append(f"{path}: {error}")
        context.close()
        browser.close()
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--skip-browser", action="store_true")
    args = parser.parse_args()
    paths = canonical_build_paths()
    errors = []
    if len(paths) != 21:
        errors.append(f"Local canonical Build inventory contains {len(paths)} pages, expected 21")
    errors.extend(validate_feeds(args.base_url))
    if not args.skip_browser and len(paths) == 21:
        errors.extend(validate_rendered_builds(args.base_url, paths))

    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if errors:
        print(json.dumps({"checkedAt": checked_at, "ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        for error in errors:
            print(f"::error::{error}")
        return 1
    print(json.dumps({"checkedAt": checked_at, "ok": True, "buildPages": len(paths)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
