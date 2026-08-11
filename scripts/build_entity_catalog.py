#!/usr/bin/env python3
"""Build the shared entity catalog used by leaderboard and Build pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "entity-catalog.json"
CHARACTER_SOURCE = ROOT / "data" / "characters.json"

WEAPONS = {
    "aegis": ("Aegis", "aegis", "Aegis.png"),
    "aura": ("Aura", "aura", "Aura.png"),
    "axe": ("Axe", "axe", "Axe.png"),
    "bananarang": ("Bananarang", "bananarang", "Bananarang.png"),
    "blackhole": ("Black Hole", "black-hole", "Black_Hole.png"),
    "bloodmagic": ("Blood Magic", "blood-magic", "Blood_Magic.png"),
    "bone": ("Bone", "bone", "Bone.png"),
    "bow": ("Bow", "bow", "Bow.png"),
    "chunkers": ("Chunkers", "chunkers", "Chunkers.png"),
    "corruptedsword": ("Corrupted Sword", "corrupted-sword", "CorruptedSword.png"),
    "dexecutioner": ("Dexecutioner", "dexecutioner", "Dexecutioner.png"),
    "dice": ("Dice", "dice", "Dice.png"),
    "dragonsbreath": ("Dragon's Breath", "dragons-breath", "Dragons_Breath.png"),
    "firestaff": ("Fire Staff", "firestaff", "Firestaff.png"),
    "flamewalker": ("Flamewalker", "flamewalker", "Flamewalker.png"),
    "frostwalker": ("Frostwalker", "frostwalker", "Frostwalker.png"),
    "herosword": ("Hero Sword", "hero-sword", "Hero_Sword.png"),
    "katana": ("Katana", "katana", "Katana.png"),
    "lightningstaff": ("Lightning Staff", "lightning-staff", "Lightning_Staff.png"),
    "mines": ("Mines", "mines", "Mines.png"),
    "poisonflask": ("Poison Flask", "poison-flask", "Poison_Flask.png"),
    "revolver": ("Revolver", "revolver", "Revolver.png"),
    "scythe": ("Scythe", "scythe", "Scythe.png"),
    "shotgun": ("Shotgun", "shotgun", "Shotgun.png"),
    "sluttyrocket": ("Slutty Rocket", "slutty-rocket", "SluttyRocket.png"),
    "sniper": ("Sniper Rifle", "sniper-rifle", "Sniper.png"),
    "spacenoodle": ("Space Noodle", "space-noodle", "Space_Noodle.png"),
    "sword": ("Sword", "sword", "Sword.png"),
    "tornado": ("Tornado", "tornado", "Tornado.png"),
    "wirelessdagger": ("Wireless Dagger", "wireless-dagger", "Wireless_Dagger.png"),
}

WEAPON_ALIASES = {
    "corruptedsword": ["cursedsword"],
    "herosword": ["herossword"],
    "mines": ["mine"],
    "sniper": ["sniperrifle"],
}

TOMES = {
    "agility": "Agility",
    "armor": "Armor",
    "attraction": "Attraction",
    "bloody": "Bloody",
    "chaos": "Chaos",
    "cooldown": "Cooldown",
    "cursed": "Cursed",
    "damage": "Damage",
    "duration": "Duration",
    "evasion": "Evasion",
    "golden": "Golden",
    "health": "Health",
    "knockback": "Knockback",
    "luck": "Luck",
    "precision": "Precision",
    "projectilespeed": "Projectile Speed",
    "quantity": "Quantity",
    "regen": "Regen",
    "shield": "Shield",
    "silver": "Silver",
    "size": "Size",
    "thorns": "Thorns",
    "xp": "XP",
}

TOME_ALIASES = {"health": ["hp", "healthtome"]}

ITEM_LABEL_OVERRIDES = {
    "bobs-light": "Bob's Light",
    "bob-dead": "Bob (Dead)",
    "cowards-cloak": "Coward's Cloak",
    "grandmas-secret-tonic": "Grandma's Secret Tonic",
    "joes-dagger": "Joe's Dagger",
    "pot-stainless-steel": "Pot (Stainless Steel)",
    "quins-mask": "Quin's Mask",
    "wizards-hat": "Wizard's Hat",
    "za-warudo": "Za Warudo",
}

ITEM_ID_OVERRIDES = {"pot-stainless-steel": "pot"}
ITEM_ALIASES = {
    "bobslight": ["boblight"],
    "pot": ["potstainlesssteel", "stainlesssteelpot"],
    "wizardshat": ["wizardhat"],
}

RUN_OBJECTIVES = {
    "cryptkey": {
        "name": "Crypt Key",
        "aliases": ["crypt key"],
        "page": "/guides/maps/graveyard/#crypt-keys",
        "image": None,
        "icon": "🔑",
        "kind": "Graveyard map objective",
    }
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def local_url(path: Path) -> str | None:
    if not path.exists():
        return None
    relative = path.relative_to(ROOT).as_posix()
    if relative.endswith("/index.html"):
        relative = relative.removesuffix("index.html")
    elif relative.endswith(".html"):
        relative = relative.removesuffix(".html")
    return "/" + relative


def page_image(page: Path) -> str | None:
    if not page.exists():
        return None
    source = page.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(
        r'(?:property=["\']og:image["\'][^>]+content|content)=["\']([^"\']+)["\']',
        source,
        flags=re.IGNORECASE,
    )
    for value in matches:
        value = html.unescape(value)
        if value.startswith("https://megabonk.org/"):
            value = value.removeprefix("https://megabonk.org")
        if value.startswith("/images/") and (ROOT / value.lstrip("/")).exists():
            return value
    return None


def make_entry(
    entity_id: str,
    label: str,
    entity_type: str,
    page: Path,
    image: Path | None,
    aliases: list[str] | None = None,
    build_url: str | None = None,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": entity_id,
        "name": label,
        "aliases": sorted(set(aliases or [])),
        "page": local_url(page),
        "image": local_url(image) if image else page_image(page),
    }
    if entity_type == "characters":
        entry["buildPage"] = build_url
    return entry


def load_reviewed_characters() -> list[dict[str, object]]:
    source = json.loads(CHARACTER_SOURCE.read_text(encoding="utf-8"))
    characters = source.get("characters", [])
    required = {
        "id", "name", "aliases", "page", "image", "buildPage",
        "difficulty", "role", "unlock", "passive", "startingWeapon",
    }
    if len(characters) != 21:
        raise ValueError(f"Expected 21 reviewed characters, found {len(characters)}")

    seen: set[str] = set()
    for entry in characters:
        missing = required.difference(entry)
        if missing:
            raise ValueError(f"Character {entry.get('id')} is missing: {sorted(missing)}")
        entity_id = str(entry["id"])
        if entity_id in seen:
            raise ValueError(f"Duplicate character id: {entity_id}")
        seen.add(entity_id)
        if entry["difficulty"] not in {"beginner", "intermediate", "advanced"}:
            raise ValueError(f"Invalid difficulty for {entity_id}: {entry['difficulty']}")
        weapon = entry["startingWeapon"]
        if not isinstance(weapon, dict) or not weapon.get("name") or not weapon.get("page"):
            raise ValueError(f"Character {entity_id} needs a starting weapon name and page")

    return sorted(characters, key=lambda entry: str(entry["name"]).lower())


def build_catalog() -> dict[str, object]:
    entities: dict[str, list[dict[str, object]]] = {
        "characters": load_reviewed_characters(),
        "weapons": [],
        "tomes": [],
        "items": [],
        "runObjectives": [],
    }

    for entity_id, (label, slug, image_name) in WEAPONS.items():
        entities["weapons"].append(
            make_entry(
                entity_id,
                label,
                "weapons",
                ROOT / "database" / "weapons" / f"{slug}.html",
                ROOT / "images" / "database" / "weapons" / image_name,
                WEAPON_ALIASES.get(entity_id),
            )
        )

    for entity_id, label in TOMES.items():
        filename = f"{label.replace(' ', '_')}_Tome.png"
        entities["tomes"].append(
            make_entry(
                entity_id,
                f"{label} Tome",
                "tomes",
                ROOT / "database" / "tomes" / f"{label.lower().replace(' ', '-')}-tome.html",
                ROOT / "images" / "Tomes" / filename,
                TOME_ALIASES.get(entity_id),
            )
        )

    item_assets = {
        normalize(path.stem.removeprefix("Item_")): path
        for path in (ROOT / "images" / "Items").glob("*.png")
    }
    for page in sorted((ROOT / "database" / "items").glob("*.html")):
        if page.stem == "index":
            continue
        slug = page.stem
        entity_id = ITEM_ID_OVERRIDES.get(slug, normalize(slug))
        label = ITEM_LABEL_OVERRIDES.get(slug, title_from_slug(slug))
        item_image = (
            item_assets.get(normalize(label))
            or item_assets.get(normalize(slug))
            or item_assets.get(entity_id)
        )
        entities["items"].append(
            make_entry(
                entity_id,
                label,
                "items",
                page,
                item_image,
                ITEM_ALIASES.get(entity_id),
            )
        )

    entities["runObjectives"] = [
        {"id": entity_id, **definition}
        for entity_id, definition in RUN_OBJECTIVES.items()
    ]

    return {
        "schemaVersion": 2,
        "generatedFrom": "Reviewed character entities, local detail pages and assets",
        "entities": entities,
    }


def main() -> int:
    catalog = build_catalog()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    counts = {
        entity_type: len(entries)
        for entity_type, entries in catalog["entities"].items()
    }
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
