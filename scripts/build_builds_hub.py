#!/usr/bin/env python3
"""Regenerate Build Hub character surfaces from the shared entity catalog."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAGE = ROOT / "guides" / "builds" / "index.html"
DEFAULT_CATALOG = ROOT / "data" / "entity-catalog.json"

OPTIONS_START = "<!-- BUILD_HUB_CHARACTER_OPTIONS_START -->"
OPTIONS_END = "<!-- BUILD_HUB_CHARACTER_OPTIONS_END -->"
CARDS_START = "<!-- BUILD_HUB_CHARACTER_CARDS_START -->"
CARDS_END = "<!-- BUILD_HUB_CHARACTER_CARDS_END -->"
ROWS_START = "<!-- BUILD_HUB_CHARACTER_ROWS_START -->"
ROWS_END = "<!-- BUILD_HUB_CHARACTER_ROWS_END -->"

# Editorial recommendations stay human-reviewed. Identity, assets and routes come
# from entity-catalog.json; a newly cataloged character is still rendered even
# before an editor adds recommendations here.
EDITORIAL = {
    "fox": ("Revolver + Bow crit/Luck", "Quantity → Damage", "Intermediate"),
    "robinette": ("Bananarang + Aegis economy", "Quantity → Cooldown", "Intermediate"),
    "roberto": ("Scythe + Hoarder economy", "Luck → Size", "Advanced"),
    "ninja": ("Katana + Dexecutioner melee", "Size → Quantity", "Advanced"),
    "megachad": ("Aura + Aegis Flex engine", "Cooldown → Size", "Beginner"),
    "birdo": ("Tornado airborne coverage", "Size → Quantity", "Intermediate"),
    "noelle": ("Frostwalker + Lightning control", "Size → Cooldown", "Beginner"),
    "dicehead": ("Dice + Revolver scaling", "XP → Luck", "Advanced"),
    "bandit": ("Dexecutioner + Katana execute", "Size → Cooldown", "Advanced"),
    "tonymczoom": ("Wireless Dagger + Lightning", "Projectile → Quantity", "Advanced"),
    "sirchadwell": ("Dexecutioner + Bananarang", "Size → Damage", "Advanced"),
    "calcium": ("Bone + Bananarang speed", "Agility → Cooldown", "Advanced"),
    "cl4nk": ("Revolver + Bow projectile crit", "Quantity → Precision", "Intermediate"),
    "monke": ("Bananarang + Revolver", "Quantity → Projectile Speed", "Intermediate"),
    "bush": ("Sniper + Bow Bullseye", "Precision → Size", "Advanced"),
    "siroofie": ("Sword + Aegis armor", "Size → Quantity", "Beginner"),
    "athena": ("Aegis + Lightning defense", "Cooldown → Agility", "Intermediate"),
    "ogre": ("Axe + Aura bruiser", "Damage → Quantity", "Beginner"),
    "amog": ("Poison Flask + Black Hole", "Cooldown → Quantity", "Intermediate"),
    "spaceman": ("Black Hole + Aura control", "XP → Quantity", "Intermediate"),
    "vlad": ("Blood Magic + Sword sustain", "Bloody → Cooldown", "Intermediate"),
}


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
    valid = [
        entry for entry in characters
        if entry.get("id") and entry.get("name") and entry.get("page")
        and entry.get("buildPage") and entry.get("image")
    ]
    if len(valid) != len(characters) or not valid:
        raise ValueError("Every catalog character needs an id, name, image, Guide and Build page")
    return valid


def render(page: str, characters: list[dict[str, object]]) -> str:
    options = "\n".join(
        f'                            <option value="{html.escape(str(entry["id"]))}">{html.escape(str(entry["name"]))}</option>'
        for entry in characters
    )
    cards = "\n".join(
        "\n".join(
            [
                f'                <article class="character-quick-card" data-character="{html.escape(str(entry["id"]))}">',
                f'                    <img src="{html.escape(str(entry["image"]))}" alt="{html.escape(str(entry["name"]))} character" width="54" height="54" loading="lazy" decoding="async">',
                "                    <div>",
                f'                        <a class="character-quick-build" href="{html.escape(str(entry["buildPage"]))}">{html.escape(str(entry["name"]))} Best Build</a>',
                f'                        <a class="character-quick-guide" href="{html.escape(str(entry["page"]))}">Character Guide</a>',
                "                    </div>",
                "                </article>",
            ]
        )
        for entry in characters
    )
    rows = []
    for entry in characters:
        entity_id = str(entry["id"])
        core, tomes, difficulty = EDITORIAL.get(
            entity_id, ("Editorial review pending", "Review pending", "Unrated")
        )
        rows.append(
            f'                            <tr data-character="{html.escape(entity_id)}">'
            f'<td class="character-name">{html.escape(str(entry["name"]))}</td>'
            f'<td>{html.escape(core)}</td><td>{html.escape(tomes)}</td><td>{html.escape(difficulty)}</td>'
            f'<td class="page-links"><a href="{html.escape(str(entry["buildPage"]))}">Build</a> · '
            f'<a href="{html.escape(str(entry["page"]))}">Guide</a></td></tr>'
        )

    page = replace_block(page, OPTIONS_START, OPTIONS_END, options)
    page = replace_block(page, CARDS_START, CARDS_END, cards)
    page = replace_block(page, ROWS_START, ROWS_END, "\n".join(rows))
    count = len(characters)
    page = re.sub(r"Compare all \d+ character Builds", f"Compare all {count} character Builds", page)
    page = re.sub(r"All \d+ Character Build Pages", f"All {count} Character Build Pages", page)
    page = re.sub(r"all \d+ Megabonk characters", f"all {count} Megabonk characters", page)
    page = re.sub(r"all \d+ character builds", f"all {count} character builds", page)
    page = re.sub(r'<div class="stat-number">\d+</div>\s*<div class="stat-label">Character Builds</div>',
                  f'<div class="stat-number">{count}</div>\n                    <div class="stat-label">Character Builds</div>', page)
    page = re.sub(r'<div class="stat-number">\d+/\d+</div>\s*<div class="stat-label">Guides Cross-Linked</div>',
                  f'<div class="stat-number">{count}/{count}</div>\n                    <div class="stat-label">Guides Cross-Linked</div>', page)
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
        print(f"Updated Build Hub for {len(characters)} catalog characters")
    else:
        print(f"Build Hub already matches {len(characters)} catalog characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
