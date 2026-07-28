#!/usr/bin/env python3
"""Fail when leaderboard entities lack a reviewed page or display asset."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEADERBOARD = ROOT / "leaderboard-data.json"
DEFAULT_CATALOG = ROOT / "data" / "entity-catalog.json"
DEFAULT_CONFIG = ROOT / "data" / "leaderboard-entity-check-config.json"


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def local_candidates(value: str) -> list[Path]:
    relative = value.split("#", 1)[0].lstrip("/")
    return [
        ROOT / relative,
        ROOT / f"{relative}.html",
        ROOT / relative / "index.html",
    ]


def page_status(value: str | None) -> tuple[bool, str | None]:
    if not value:
        return False, "missing page"
    candidates = local_candidates(value)
    existing = next((candidate for candidate in candidates if candidate.is_file()), None)
    if not existing:
        return False, f"page file not found: {value}"
    if "#" in value:
        anchor = value.split("#", 1)[1]
        source = existing.read_text(encoding="utf-8", errors="ignore")
        if not re.search(rf'\bid=["\']{re.escape(anchor)}["\']', source):
            return False, f"page anchor not found: {value}"
    return True, None


def asset_status(entry: dict[str, Any]) -> tuple[bool, str | None]:
    image = entry.get("image")
    if image:
        if any(candidate.is_file() for candidate in local_candidates(image)):
            return True, None
        return False, f"image file not found: {image}"
    if entry.get("icon"):
        return True, None
    return False, "missing image or fallback icon"


def build_indexes(catalog: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    indexes: dict[str, dict[str, dict[str, Any]]] = {}
    for entity_type, entries in catalog.get("entities", {}).items():
        index: dict[str, dict[str, Any]] = {}
        for entry in entries:
            for key in (entry.get("id"), entry.get("name"), *entry.get("aliases", [])):
                if key:
                    index[normalize(key)] = entry
        indexes[entity_type] = index
    return indexes


def observed_values(records: list[dict[str, Any]]) -> dict[str, set[str]]:
    values = {
        "characters": set(),
        "weapons": set(),
        "tomes": set(),
        "items": set(),
    }
    for record in records:
        if record.get("character"):
            values["characters"].add(record["character"])
        for entity_type in ("weapons", "tomes", "items"):
            values[entity_type].update(record.get(entity_type) or [])
    return values


def known_gap_rules(config: dict[str, Any]) -> dict[tuple[str, str], set[str]]:
    return {
        (rule["sourceType"], normalize(rule["id"])): set(rule.get("allow", []))
        for rule in config.get("knownGaps", [])
        if rule.get("sourceType") and rule.get("id")
    }


def check_entities(
    leaderboard: dict[str, Any],
    catalog: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    records = leaderboard.get("data", [])
    indexes = build_indexes(catalog)
    observed = observed_values(records)
    run_objectives = indexes.get("runObjectives", {})
    rules = known_gap_rules(config or {})
    gaps: list[dict[str, Any]] = []
    known_gaps: list[dict[str, Any]] = []

    for entity_type, values in observed.items():
        for raw_value in sorted(values, key=normalize):
            key = normalize(raw_value)
            resolved_type = entity_type
            entry = indexes.get(entity_type, {}).get(key)
            if not entry and entity_type == "items":
                entry = run_objectives.get(key)
                if entry:
                    resolved_type = "runObjectives"
            if not entry:
                gaps.append(
                    {
                        "sourceType": entity_type,
                        "id": raw_value,
                        "reason": "unregistered entity",
                    }
                )
                continue

            page_ok, page_reason = page_status(entry.get("page"))
            asset_ok, asset_reason = asset_status(entry)
            failures = [
                (kind, reason)
                for kind, ok, reason in (
                    ("page", page_ok, page_reason),
                    ("asset", asset_ok, asset_reason),
                )
                if not ok and reason
            ]
            allowed = rules.get((entity_type, key), set())
            blocking = [reason for kind, reason in failures if kind not in allowed]
            acknowledged = [reason for kind, reason in failures if kind in allowed]
            base = {
                "sourceType": entity_type,
                "resolvedType": resolved_type,
                "id": raw_value,
                "name": entry.get("name"),
            }
            if blocking:
                gaps.append({**base, "reason": "; ".join(blocking)})
            if acknowledged:
                known_gaps.append({**base, "reason": "; ".join(acknowledged)})

    return {
        "schemaVersion": 1,
        "checkedAt": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "recordCount": len(records),
        "observedCounts": {
            entity_type: len(values) for entity_type, values in observed.items()
        },
        "gapCount": len(gaps),
        "knownGapCount": len(known_gaps),
        "gaps": gaps,
        "knownGaps": known_gaps,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leaderboard", type=Path, default=DEFAULT_LEADERBOARD)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    config = load_json(args.config) if args.config.exists() else {}
    report = check_entities(
        load_json(args.leaderboard), load_json(args.catalog), config
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    for gap in report["knownGaps"]:
        print(
            f"::warning::Known leaderboard entity gap: "
            f"{gap['sourceType']}:{gap['id']} - {gap['reason']}"
        )
    if report["gapCount"]:
        print(
            f"::error::Leaderboard entity coverage failed with "
            f"{report['gapCount']} blocking gap(s)."
        )
        return 1
    print("Leaderboard entity coverage is complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
