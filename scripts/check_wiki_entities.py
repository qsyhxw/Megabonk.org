#!/usr/bin/env python3
"""Compare Megabonk Wiki entity categories with the reviewed local catalog.

The monitor never publishes an HTML detail page. It creates structured review
drafts and may download an image only when the file page exposes an allowlisted
license. Existing reviewed pages with a missing image can receive that image at
their already-declared local path; new entities stay in the imported staging
directory until their facts are independently checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://megabonk.wiki/api.php"
WIKI_BASE = "https://megabonk.wiki/wiki/"
CATALOG_PATH = ROOT / "data" / "entity-catalog.json"
SNAPSHOT_PATH = ROOT / "data" / "wiki-entity-snapshot.json"
REPORT_PATH = ROOT / "data" / "wiki-entity-sync-report.json"
ATTRIBUTION_PATH = ROOT / "data" / "wiki-image-attribution.json"
DRAFT_ROOT = ROOT / "data" / "entity-drafts"
USER_AGENT = (
    "Mozilla/5.0 (compatible; Megabonk.org entity monitor; "
    "+https://megabonk.org/)"
)

CATEGORIES = {
    "characters": "Category:Characters",
    "weapons": "Category:Weapons",
    "tomes": "Category:Tomes",
    "items": "Category:Items",
}

LICENSE_ALLOWLIST = {
    "cc0",
    "cc by 4.0",
    "cc by-sa 4.0",
    "cc by-sa 3.0",
    "public domain",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def request_json(parameters: dict[str, str]) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {"format": "json", "formatversion": "2", **parameters}
    )
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def category_members(category: str) -> list[str]:
    members: list[str] = []
    continuation: str | None = None
    while True:
        parameters = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmnamespace": "0",
            "cmlimit": "max",
        }
        if continuation:
            parameters["cmcontinue"] = continuation
        payload = request_json(parameters)
        members.extend(
            item["title"]
            for item in payload.get("query", {}).get("categorymembers", [])
            if item.get("title")
        )
        continuation = payload.get("continue", {}).get("cmcontinue")
        if not continuation:
            return sorted(set(members))


def page_images(titles: list[str]) -> dict[str, dict[str, str]]:
    results: dict[str, dict[str, str]] = {}
    for offset in range(0, len(titles), 40):
        payload = request_json(
            {
                "action": "query",
                "prop": "pageimages",
                "titles": "|".join(titles[offset : offset + 40]),
                "piprop": "name|original",
            }
        )
        for page in payload.get("query", {}).get("pages", []):
            original = page.get("original") or {}
            if page.get("title") and page.get("pageimage") and original.get("source"):
                results[page["title"]] = {
                    "fileTitle": f"File:{page['pageimage']}",
                    "sourceUrl": original["source"],
                }
    return results


def image_license(file_title: str) -> dict[str, str]:
    payload = request_json(
        {
            "action": "query",
            "prop": "imageinfo",
            "titles": file_title,
            "iiprop": "url|extmetadata",
        }
    )
    pages = payload.get("query", {}).get("pages", [])
    info = (pages[0].get("imageinfo") or [{}])[0] if pages else {}
    metadata = info.get("extmetadata") or {}

    def value(key: str) -> str:
        raw = metadata.get(key) or {}
        return re.sub(r"<[^>]+>", "", str(raw.get("value") or "")).strip()

    return {
        "sourceUrl": info.get("url") or "",
        "descriptionUrl": info.get("descriptionurl") or "",
        "license": value("LicenseShortName") or value("UsageTerms"),
        "artist": value("Artist"),
        "credit": value("Credit"),
    }


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def catalog_indexes(catalog: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    indexes = {}
    for entity_type, entries in catalog.get("entities", {}).items():
        index: dict[str, dict[str, Any]] = {}
        for entry in entries:
            for key in (entry["id"], entry["name"], *entry.get("aliases", [])):
                index[normalize(key)] = entry
        indexes[entity_type] = index
    return indexes


def declared_missing_image_path(entry: dict[str, Any]) -> Path | None:
    page = entry.get("page")
    if not page:
        return None
    relative = page.lstrip("/")
    candidates = [ROOT / relative, ROOT / f"{relative}.html", ROOT / relative / "index.html"]
    html_path = next((path for path in candidates if path.exists()), None)
    if not html_path:
        return None
    source = html_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        source,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    value = match.group(1).removeprefix("https://megabonk.org").lstrip("/")
    if not value.startswith("images/"):
        return None
    return ROOT / value


def safe_extension(url: str) -> str | None:
    extension = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return extension
    guessed = mimetypes.guess_extension(mimetypes.guess_type(url)[0] or "")
    return guessed if guessed in {".png", ".jpg", ".jpeg", ".webp"} else None


def download_image(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        content = response.read(5_000_001)
    if len(content) > 5_000_000:
        raise ValueError("Image exceeds the 5 MB safety limit")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-licensed-images", action="store_true")
    args = parser.parse_args()

    catalog = load_json(CATALOG_PATH, {})
    if not catalog:
        raise ValueError(f"Missing catalog: {CATALOG_PATH}")
    indexes = catalog_indexes(catalog)

    remote = {
        entity_type: category_members(category)
        for entity_type, category in CATEGORIES.items()
    }
    all_titles = [title for titles in remote.values() for title in titles]
    images = page_images(all_titles)

    previous = load_json(SNAPSHOT_PATH, {})
    previous_remote = previous.get("entities", {})
    first_run = not bool(previous_remote)

    gaps: list[dict[str, Any]] = []
    missing_images: list[dict[str, Any]] = []
    for entity_type, titles in remote.items():
        index = indexes.get(entity_type, {})
        for title in titles:
            entry = index.get(normalize(title))
            wiki_url = WIKI_BASE + urllib.parse.quote(title.replace(" ", "_"))
            candidate = images.get(title)
            if not entry:
                gaps.append(
                    {
                        "type": entity_type,
                        "name": title,
                        "wikiUrl": wiki_url,
                        "imageCandidate": candidate,
                    }
                )
            elif not entry.get("image"):
                missing_images.append(
                    {
                        "type": entity_type,
                        "name": title,
                        "entityId": entry["id"],
                        "page": entry.get("page"),
                        "wikiUrl": wiki_url,
                        "imageCandidate": candidate,
                    }
                )

    def flattened(values: dict[str, list[str]]) -> set[tuple[str, str]]:
        return {
            (entity_type, title)
            for entity_type, titles in values.items()
            for title in titles
        }

    current_set = flattened(remote)
    previous_set = flattened(previous_remote) if previous_remote else set()
    new_entities = sorted(current_set - previous_set) if not first_run else []
    removed_entities = sorted(previous_set - current_set) if not first_run else []

    attribution = load_json(ATTRIBUTION_PATH, {"schemaVersion": 1, "images": []})
    attribution_by_path = {
        item["localPath"]: item for item in attribution.get("images", [])
    }
    downloaded: list[dict[str, str]] = []

    if args.download_licensed_images:
        for candidate_entry in [*gaps, *missing_images]:
            candidate = candidate_entry.get("imageCandidate")
            if not candidate:
                continue
            license_info = image_license(candidate["fileTitle"])
            license_name = license_info["license"].lower()
            extension = safe_extension(license_info["sourceUrl"])
            if license_name not in LICENSE_ALLOWLIST or not extension:
                candidate_entry["imageStatus"] = "manual-license-review"
                candidate_entry["license"] = license_info
                continue

            local_entry = indexes.get(candidate_entry["type"], {}).get(
                normalize(candidate_entry["name"])
            )
            destination = (
                declared_missing_image_path(local_entry)
                if local_entry
                else ROOT
                / "images"
                / "imported"
                / "megabonk-wiki"
                / candidate_entry["type"]
                / f"{slugify(candidate_entry['name'])}{extension}"
            )
            if not destination:
                continue
            if not destination.exists():
                download_image(license_info["sourceUrl"], destination)
            local_path = "/" + destination.relative_to(ROOT).as_posix()
            candidate_entry["imageStatus"] = "downloaded-licensed"
            candidate_entry["localImage"] = local_path
            record = {
                "localPath": local_path,
                "entity": candidate_entry["name"],
                "entityType": candidate_entry["type"],
                "wikiPage": candidate_entry["wikiUrl"],
                "filePage": license_info["descriptionUrl"],
                "sourceUrl": license_info["sourceUrl"],
                "license": license_info["license"],
                "artist": license_info["artist"],
                "credit": license_info["credit"],
            }
            attribution_by_path[local_path] = record
            downloaded.append(record)

    if downloaded:
        attribution["images"] = sorted(
            attribution_by_path.values(), key=lambda item: item["localPath"]
        )
        write_json(ATTRIBUTION_PATH, attribution)

    for gap in gaps:
        draft_path = DRAFT_ROOT / gap["type"] / f"{slugify(gap['name'])}.json"
        if not draft_path.exists():
            write_json(
                draft_path,
                {
                    "status": "needs-review",
                    "entityType": gap["type"],
                    "name": gap["name"],
                    "wikiPage": gap["wikiUrl"],
                    "candidateImage": gap.get("localImage"),
                    "requiredChecks": [
                        "Confirm the entity exists in the current game version",
                        "Verify effects, unlock conditions and numbers with two independent sources",
                        "Confirm image attribution before public use",
                        "Create a full task-focused page only when it satisfies the site page requirements",
                    ],
                },
            )

    comparison_payload = {
        "remote": remote,
        "gaps": [(item["type"], item["name"]) for item in gaps],
        "missingImages": [
            (item["type"], item["name"]) for item in missing_images
        ],
    }
    comparison_fingerprint = hashlib.sha256(
        json.dumps(comparison_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    previous_fingerprint = previous.get("comparisonFingerprint")
    files_changed = (
        first_run
        or comparison_fingerprint != previous_fingerprint
        or bool(downloaded)
        or bool(new_entities)
        or bool(removed_entities)
    )

    checked_at = utc_now()
    if files_changed:
        write_json(
            SNAPSHOT_PATH,
            {
                "schemaVersion": 1,
                "source": API_URL,
                "checkedAt": checked_at,
                "comparisonFingerprint": comparison_fingerprint,
                "entities": remote,
            },
        )
        write_json(
            REPORT_PATH,
            {
                "schemaVersion": 1,
                "checkedAt": checked_at,
                "source": API_URL,
                "baselineCreated": first_run,
                "newSincePrevious": [
                    {"type": entity_type, "name": name}
                    for entity_type, name in new_entities
                ],
                "removedSincePrevious": [
                    {"type": entity_type, "name": name}
                    for entity_type, name in removed_entities
                ],
                "catalogGaps": gaps,
                "localPagesMissingImages": missing_images,
                "downloadedLicensedImages": downloaded,
                "publishingPolicy": (
                    "New entities create review drafts only. Public HTML requires "
                    "independent fact checking and the site page-creation standard."
                ),
            },
        )

    result = {
        "files_changed": files_changed,
        "baseline_created": first_run,
        "new_count": len(new_entities),
        "removed_count": len(removed_entities),
        "catalog_gap_count": len(gaps),
        "missing_image_count": len(missing_images),
        "downloaded_image_count": len(downloaded),
    }
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
