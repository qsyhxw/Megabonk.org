#!/usr/bin/env python3
"""Regenerate the Characters Hub from the shared entity catalog."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAGE = ROOT / "guides" / "characters" / "index.html"
DEFAULT_CATALOG = ROOT / "data" / "entity-catalog.json"

ROWS_START = "<!-- CHARACTER_HUB_ROWS_START -->"
ROWS_END = "<!-- CHARACTER_HUB_ROWS_END -->"
ITEMLIST_START = "<!-- CHARACTER_HUB_ITEMLIST_START -->"
ITEMLIST_END = "<!-- CHARACTER_HUB_ITEMLIST_END -->"


def replace_block(source: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{body}\n{end}"
    updated, count = pattern.subn(lambda _: replacement, source, count=1)
    if count != 1:
        raise ValueError(f"Missing or duplicate generated block: {start}")
    return updated


def load_characters(catalog_path: Path) -> list[dict[str, object]]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    characters = catalog.get("entities", {}).get("characters", [])
    required = {
        "id", "name", "aliases", "page", "image", "buildPage",
        "difficulty", "role", "unlock", "passive", "startingWeapon",
    }
    if len(characters) != 21:
        raise ValueError(f"Characters Hub requires 21 reviewed entities, found {len(characters)}")
    for entry in characters:
        missing = required.difference(entry)
        if missing:
            raise ValueError(f"Character {entry.get('id')} is missing: {sorted(missing)}")
        weapon = entry["startingWeapon"]
        if not isinstance(weapon, dict) or not weapon.get("name") or not weapon.get("page"):
            raise ValueError(f"Character {entry['id']} needs a starting weapon name and page")
    return characters


def render_item_list(characters: list[dict[str, object]]) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Megabonk Character Guides",
        "numberOfItems": len(characters),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": f'{entry["name"]} Character Guide',
                "url": f'https://megabonk.org{entry["page"]}',
            }
            for position, entry in enumerate(characters, start=1)
        ],
    }
    return (
        '    <script type="application/ld+json">\n'
        + "    "
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "\n    </script>"
    )


def render_rows(characters: list[dict[str, object]]) -> str:
    rows = []
    for entry in characters:
        weapon = entry["startingWeapon"]
        searchable = " ".join(
            str(value)
            for value in (
                entry["name"], *entry.get("aliases", []), entry["role"],
                entry["unlock"], entry["passive"], weapon["name"],
            )
        ).lower()
        searchable = re.sub(r"\s+", " ", searchable).strip()
        rows.append(
            "\n".join(
                [
                    f'                        <tr data-character-id="{html.escape(str(entry["id"]))}" data-difficulty="{html.escape(str(entry["difficulty"]))}" data-role="{html.escape(str(entry["role"]))}" data-search="{html.escape(searchable)}">',
                    f'                            <td><div class="character-cell"><img src="{html.escape(str(entry["image"]))}" alt="{html.escape(str(entry["name"]))}" width="48" height="48" loading="lazy" decoding="async"><a href="{html.escape(str(entry["page"]))}">{html.escape(str(entry["name"]))}</a></div></td><td>{html.escape(str(entry["unlock"]))}</td><td>{html.escape(str(entry["passive"]))}</td><td><a href="{html.escape(str(weapon["page"]))}">{html.escape(str(weapon["name"]))}</a></td><td><a class="table-action" href="{html.escape(str(entry["page"]))}">Character Guide</a></td><td><a class="table-action" href="{html.escape(str(entry["buildPage"]))}">Best Build</a></td>',
                    "                        </tr>",
                ]
            )
        )
    return "\n".join(rows)


def render(page: str, characters: list[dict[str, object]]) -> str:
    page = replace_block(page, ITEMLIST_START, ITEMLIST_END, render_item_list(characters))
    page = replace_block(page, ROWS_START, ROWS_END, render_rows(characters))
    count = len(characters)
    page = re.sub(r"Showing <strong id=\"visibleCount\">\d+</strong> of <strong>\d+</strong>", f'Showing <strong id="visibleCount">{count}</strong> of <strong>{count}</strong>', page)
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", type=Path, default=DEFAULT_PAGE)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    characters = load_characters(args.catalog)
    source = args.page.read_text(encoding="utf-8")
    rendered = render(source, characters)
    if rendered != source:
        args.page.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Updated Characters Hub for {len(characters)} catalog characters")
    else:
        print(f"Characters Hub already matches {len(characters)} catalog characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
