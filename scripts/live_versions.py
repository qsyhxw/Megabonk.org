"""Auto-synced version labels (SOP 05 §2.9 AUTO_SYNC). Data: data/live-versions.json.

Generators render these spans; scripts/sync_live_versions.py rewrites only their text.
"""
import json
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data' / 'live-versions.json'


def load():
    return json.loads(DATA.read_text(encoding='utf8'))


def long_date(iso):
    d = date.fromisoformat(iso)
    return f'{d.day} {d:%B %Y}'


def value(key):
    return f'<strong data-live="{key}">{load()[key]["value"]}</strong>'


def when(key):
    return f'<span data-live-date="{key}">{long_date(load()[key]["date"])}</span>'
