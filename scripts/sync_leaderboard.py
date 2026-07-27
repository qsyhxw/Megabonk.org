#!/usr/bin/env python3
"""Sync the public Megabonk community leaderboard into stable site JSON.

The source is a Nuxt SSR page. Its ``__NUXT_DATA__`` payload contains the
verified run records, including source submission timestamps and build data.
This script keeps those source timestamps and adds crawl-observation fields so
the site can power all-time, today, recent, and meta-build views from one file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCE_URL = "https://megabonk.leaderboard.gg/"
DEFAULT_OUTPUT = Path("leaderboard-data.json")
DEFAULT_META_OUTPUT = Path("data/leaderboard-meta.json")
MINIMUM_VALID_RECORDS = 100
USER_AGENT = (
    "Mozilla/5.0 (compatible; Megabonk.org leaderboard sync; "
    "+https://megabonk.org/leaderboard/)"
)

SPECIAL_VALUES = {
    -1: None,
    -2: math.nan,
    -3: math.inf,
    -4: -math.inf,
    -5: -0.0,
}


class NuxtPayloadDecoder:
    """Decode Nuxt/devalue's flattened JSON payload."""

    def __init__(self, values: list[Any]):
        self.values = values
        self.memo: dict[int, Any] = {}

    def decode_reference(self, value: Any) -> Any:
        if isinstance(value, bool) or not isinstance(value, int):
            return value
        if value < 0:
            return SPECIAL_VALUES.get(value)
        return self.decode_index(value)

    def decode_index(self, index: int) -> Any:
        if index in self.memo:
            return self.memo[index]

        raw = self.values[index]
        if raw is None or isinstance(raw, (str, int, float, bool)):
            self.memo[index] = raw
            return raw

        if isinstance(raw, list):
            if raw and isinstance(raw[0], str):
                tag = raw[0]
                if tag in {"Reactive", "ShallowReactive", "Ref", "ShallowRef"}:
                    value = self.decode_reference(raw[1])
                elif tag == "Date":
                    value = self.decode_reference(raw[1])
                elif tag == "Set":
                    value = [self.decode_reference(item) for item in raw[1:]]
                elif tag == "Map":
                    value = {
                        self.decode_reference(raw[i]): self.decode_reference(raw[i + 1])
                        for i in range(1, len(raw), 2)
                    }
                elif tag == "BigInt":
                    value = int(self.decode_reference(raw[1]))
                else:
                    value = [self.decode_reference(item) for item in raw[1:]]
                self.memo[index] = value
                return value

            value: list[Any] = []
            self.memo[index] = value
            value.extend(self.decode_reference(item) for item in raw)
            return value

        if isinstance(raw, dict):
            value_dict: dict[str, Any] = {}
            self.memo[index] = value_dict
            value_dict.update(
                {key: self.decode_reference(item) for key, item in raw.items()}
            )
            return value_dict

        raise TypeError(f"Unsupported Nuxt payload value: {type(raw)!r}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def firestore_time_to_iso(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    seconds = value.get("_seconds")
    if not isinstance(seconds, (int, float)):
        return None
    return (
        datetime.fromtimestamp(seconds, tz=timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def version_number_to_string(value: Any) -> str | None:
    if not isinstance(value, int):
        return str(value) if value else None
    if value < 10_000_000_000:
        return str(value)
    major = value // 10_000_000_000
    remainder = value % 10_000_000_000
    minor = remainder // 100_000
    patch = remainder % 100_000
    return f"{major}.{minor}.{patch}"


def unique_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return list(dict.fromkeys(value for value in values if isinstance(value, str) and value))


def fetch_source_html() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read().decode("utf-8")
        except Exception as error:  # pragma: no cover - network fallback
            last_error = error
            time.sleep(2 * (attempt + 1))

    try:  # Cloudflare/browser fallback used by the existing workflow.
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT, viewport={"width": 1400, "height": 900})
            page.goto(SOURCE_URL, timeout=90_000, wait_until="domcontentloaded")
            page.wait_for_selector("#__NUXT_DATA__", timeout=60_000)
            html = page.content()
            browser.close()
            return html
    except Exception as fallback_error:  # pragma: no cover - network failure
        raise RuntimeError(
            f"Unable to fetch {SOURCE_URL}: {last_error}; browser fallback: {fallback_error}"
        ) from fallback_error


def decode_source(html: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    match = re.search(
        r'<script[^>]+id="__NUXT_DATA__"[^>]*>(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("Nuxt SSR payload was not found")
    values = json.loads(match.group(1))
    root = NuxtPayloadDecoder(values).decode_index(0)
    records = root.get("data", {}).get("leaderboard")
    state = root.get("state", {})
    if not isinstance(records, list):
        raise ValueError("Leaderboard array was not found in Nuxt payload")
    return records, state


def source_fingerprint(records: list[dict[str, Any]]) -> str:
    """Return a stable digest so same-count record edits still publish."""
    serialized = json.dumps(
        records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def previous_record_index(output_path: Path) -> dict[str, dict[str, Any]]:
    if not output_path.exists():
        return {}
    try:
        previous = json.loads(output_path.read_text(encoding="utf-8")).get("data", [])
    except (json.JSONDecodeError, OSError):
        return {}

    index: dict[str, dict[str, Any]] = {}
    for record in previous:
        keys = [
            record.get("submissionId"),
            record.get("id"),
            record.get("videoURL"),
        ]
        for key in keys:
            if key:
                index[str(key)] = record
    return index


def load_previous_payload(output_path: Path) -> dict[str, Any]:
    if not output_path.exists():
        return {}
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def normalize_records(
    records: list[dict[str, Any]],
    previous: dict[str, dict[str, Any]],
    observed_at: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for source_record in records:
        submission_id = source_record.get("submissionId")
        source_id = source_record.get("id")
        video_url = source_record.get("videoURL")
        old = (
            previous.get(str(submission_id))
            or previous.get(str(source_id))
            or previous.get(str(video_url))
            or {}
        )

        created_raw = source_record.get("createdAt")
        updated_raw = source_record.get("updatedAt")
        rank = int(source_record.get("rank") or 0)
        previous_rank = old.get("rank")
        rank_change = (
            int(previous_rank) - rank
            if isinstance(previous_rank, int) and rank > 0
            else None
        )

        normalized.append(
            {
                "id": source_id,
                "submissionId": submission_id,
                "rank": rank,
                "previousRank": previous_rank,
                "rankChange": rank_change,
                "playerName": source_record.get("playerName") or "Anonymous",
                "videoURL": video_url or "",
                "country": source_record.get("country"),
                "character": source_record.get("character") or "",
                "kills": int(source_record.get("kills") or 0),
                "userId": source_record.get("userId"),
                "buildVersion": source_record.get("buildVersion"),
                "buildVersionLabel": version_number_to_string(
                    source_record.get("buildVersion")
                ),
                "map": source_record.get("map"),
                "weapons": unique_strings(source_record.get("weapons")),
                "tomes": unique_strings(source_record.get("tomes")),
                "items": unique_strings(source_record.get("items")),
                "stats": source_record.get("stats") or {},
                "socials": source_record.get("socials") or None,
                "createdAt": created_raw,
                "createdAtIso": firestore_time_to_iso(created_raw),
                "updatedAt": updated_raw,
                "updatedAtIso": firestore_time_to_iso(updated_raw),
                "firstSeenAt": old.get("firstSeenAt") or observed_at,
                "lastSeenAt": observed_at,
            }
        )
    return normalized


def validate(records: list[dict[str, Any]]) -> None:
    if len(records) < MINIMUM_VALID_RECORDS:
        raise ValueError(
            f"Only {len(records)} records found; refusing to replace known-good data"
        )
    ranks = [record["rank"] for record in records]
    if len(ranks) != len(set(ranks)) or min(ranks) != 1:
        raise ValueError("Ranks are missing or duplicated")
    required = ("submissionId", "playerName", "character", "kills", "createdAt")
    invalid = [
        record.get("rank")
        for record in records
        if any(record.get(field) in (None, "") for field in required)
    ]
    if invalid:
        raise ValueError(f"Required fields are missing at ranks: {invalid[:10]}")


def top_values(records: list[dict[str, Any]], field: str, limit: int = 8) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for record in records:
        values = record.get(field, [])
        if isinstance(values, list):
            counts.update(set(values))
    sample_size = len(records)
    return [
        {
            "id": value,
            "runs": count,
            "usageRate": round(count / sample_size, 4) if sample_size else 0,
        }
        for value, count in counts.most_common(limit)
    ]


def build_meta(
    records: list[dict[str, Any]],
    observed_at: str,
    active_version: str | None,
) -> dict[str, Any]:
    current = [
        record
        for record in records
        if not active_version or record.get("buildVersionLabel") == active_version
    ]
    if not current:
        current = records

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in current:
        grouped[record["character"]].append(record)

    characters = []
    for character, runs in grouped.items():
        runs.sort(key=lambda record: record["kills"], reverse=True)
        scores = [record["kills"] for record in runs]
        characters.append(
            {
                "character": character,
                "sampleSize": len(runs),
                "topScore": max(scores),
                "medianScore": int(statistics.median(scores)),
                "topWeapons": top_values(runs, "weapons", 6),
                "topTomes": top_values(runs, "tomes", 6),
                "topItems": top_values(runs, "items", 8),
                "representativeRuns": [
                    {
                        "rank": run["rank"],
                        "playerName": run["playerName"],
                        "kills": run["kills"],
                        "weapons": run["weapons"],
                        "tomes": run["tomes"],
                        "videoURL": run["videoURL"],
                        "submissionId": run["submissionId"],
                    }
                    for run in runs[:3]
                ],
            }
        )
    characters.sort(key=lambda item: (-item["sampleSize"], -item["topScore"]))

    return {
        "source": "Leaderboard.gg Megabonk community leaderboard",
        "sourceUrl": SOURCE_URL,
        "generatedAt": observed_at,
        "activeVersion": active_version,
        "sampleSize": len(current),
        "methodology": (
            "Observed verified leaderboard runs for the active leaderboard version. "
            "Usage frequency is evidence, not an automatic editorial recommendation."
        ),
        "overall": {
            "topWeapons": top_values(current, "weapons"),
            "topTomes": top_values(current, "tomes"),
            "topItems": top_values(current, "items"),
        },
        "characters": characters,
    }


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-html", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--meta-output", type=Path, default=DEFAULT_META_OUTPUT)
    args = parser.parse_args()

    html = (
        args.input_html.read_text(encoding="utf-8")
        if args.input_html
        else fetch_source_html()
    )
    source_records, state = decode_source(html)
    source_digest = source_fingerprint(source_records)
    observed_at = utc_now()
    previous_payload = load_previous_payload(args.output)
    source_version = state.get("$sleaderboardVersion")
    if (
        previous_payload.get("source_url") == SOURCE_URL
        and previous_payload.get("source_fingerprint") == source_digest
    ):
        print(
            f"No leaderboard change detected ({len(source_records)} records, "
            f"version {source_version}); keeping existing files"
        )
        return 0

    previous = previous_record_index(args.output)
    records = normalize_records(source_records, previous, observed_at)
    validate(records)

    active_version = state.get("$sbuildVersion")
    output = {
        "source": "Leaderboard.gg Megabonk community leaderboard",
        "source_url": SOURCE_URL,
        "fetched_at": observed_at,
        "active_version": active_version,
        "leaderboard_version": source_version,
        "source_fingerprint": source_digest,
        "count": len(records),
        "data": records,
    }
    meta = build_meta(records, observed_at, active_version)
    write_json_atomic(args.output, output)
    write_json_atomic(args.meta_output, meta)
    print(
        f"Synced {len(records)} records for version {active_version or 'unknown'} "
        f"to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
