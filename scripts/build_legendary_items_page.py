#!/usr/bin/env python3
"""Generate Legendary item facts from the catalog while preserving editorial tiers."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "entity-catalog.json"
RANKINGS = ROOT / "data" / "legendary-item-rankings.json"
PAGE = ROOT / "tier-lists" / "legendary-items" / "index.html"
ITEMLIST_START = "<!-- GENERATED:LEGENDARY_ITEMLIST:START -->"
ITEMLIST_END = "<!-- GENERATED:LEGENDARY_ITEMLIST:END -->"
ROWS_START = "<!-- GENERATED:LEGENDARY_ROWS:START -->"
ROWS_END = "<!-- GENERATED:LEGENDARY_ROWS:END -->"


def replace_region(source: str, start: str, end: str, content: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Expected one generated region: {start}")
    before, remainder = source.split(start, 1)
    _, after = remainder.split(end, 1)
    return f"{before}{start}\n{content}\n    {end}{after}"


def load_inputs() -> tuple[dict[str, dict[str, object]], list[dict[str, str]]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    items = {
        str(item["id"]): item
        for item in catalog["entities"]["items"]
        if item.get("rarity") == "Legendary"
    }
    editorial = json.loads(RANKINGS.read_text(encoding="utf-8"))["rankings"]
    ranked_ids = [str(entry["id"]) for entry in editorial]
    if len(ranked_ids) != len(set(ranked_ids)):
        raise ValueError("Legendary editorial ranking contains duplicate ids")
    if set(ranked_ids) != set(items):
        raise ValueError(
            "Legendary roster changed; manually review tiers before publishing. "
            f"unranked={sorted(set(items) - set(ranked_ids))}, "
            f"no_longer_legendary={sorted(set(ranked_ids) - set(items))}"
        )
    for entity_id, item in items.items():
        for field in ("name", "page", "image", "rarity", "effect", "unlock"):
            if not item.get(field):
                raise ValueError(f"Legendary item {entity_id} is missing {field}")
        page = ROOT / f"{str(item['page']).lstrip('/')}.html"
        image = ROOT / str(item["image"]).lstrip("/")
        if not page.is_file():
            raise ValueError(f"Legendary item {entity_id} detail page is missing: {page}")
        if not image.is_file():
            raise ValueError(f"Legendary item {entity_id} image is missing: {image}")
    return items, editorial


def itemlist_schema(items: dict[str, dict[str, object]], editorial: list[dict[str, str]]) -> str:
    elements = [
        {
            "@type": "ListItem",
            "position": position,
            "name": items[entry["id"]]["name"],
            "url": f"https://megabonk.org{items[entry['id']]['page']}",
        }
        for position, entry in enumerate(editorial, 1)
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Megabonk Legendary Items Ranked",
        "numberOfItems": len(elements),
        "itemListElement": elements,
    }
    payload = json.dumps(schema, ensure_ascii=False, indent=6)
    return f'    <script type="application/ld+json">\n{payload}\n    </script>'


def table_rows(items: dict[str, dict[str, object]], editorial: list[dict[str, str]]) -> str:
    rows: list[str] = []
    for entry in editorial:
        item = items[entry["id"]]
        tier = entry["tier"].lower()
        values = {
            "tier": html.escape(entry["tier"]),
            "tier_class": html.escape(tier),
            "image": html.escape(str(item["image"]), quote=True),
            "page": html.escape(str(item["page"]), quote=True),
            "name": html.escape(str(item["name"])),
            "effect": html.escape(str(item["effect"])),
            "unlock": html.escape(str(item["unlock"])),
            "build": html.escape(entry["buildUse"]),
            "reason": html.escape(entry["reason"]),
        }
        rows.append(
            '                        <tr data-item-id="{id}"><td><span class="tier {tier_class}">{tier}</span></td>'
            '<td><span class="entity"><img src="{image}" alt="" width="44" height="44" loading="lazy">'
            '<a href="{page}">{name}</a></span></td><td>{effect}</td><td>{unlock}</td>'
            '<td><strong>{build}</strong><br><span class="muted">{reason}</span></td></tr>'.format(
                id=html.escape(entry["id"], quote=True), **values
            )
        )
    return "\n".join(rows)


def render(source: str) -> str:
    items, editorial = load_inputs()
    source = replace_region(source, ITEMLIST_START, ITEMLIST_END, itemlist_schema(items, editorial))
    source = replace_region(source, ROWS_START, ROWS_END, table_rows(items, editorial))
    source = source.replace("22 ranked items", f"{len(editorial)} ranked items")
    source = source.replace(
        "Giant Fork is a high-value choice once Crit is established, while Overpowered Lamp, Anvil, Pot, Wizard's Hat, Joe's Dagger and Sucky Magnet can be stronger for their matching build or run length.",
        "Overpowered Lamp is a leading proc pick when supported on-hit effects are already online. Anvil, Pot, Joe's Dagger and Sucky Magnet can be stronger in longer specialized runs.",
    )
    return source


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    original = PAGE.read_text(encoding="utf-8")
    generated = render(original)
    if args.check:
        if generated != original:
            raise SystemExit("Legendary Items page is not synchronized; run build_legendary_items_page.py")
        print("Legendary Items page is synchronized")
        return 0
    PAGE.write_text(generated, encoding="utf-8")
    print(f"Wrote {PAGE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
