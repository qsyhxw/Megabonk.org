"""Build data/pokebonk-s3-reference.json from the Season 3 public-client extraction.

Inputs (written by scripts/pokebonk_sync_source.cjs and scripts/pokebonk_s3_extract.cjs):
  _private/pb-candidate.json  League (138), items, Lab, news from the config chunk
  _private/pb-s3.json         species, English passives, move runtimes, fusions
Output keeps the field shapes of data/pokebonk-tools-reference.json so the loadout
and tier generators can read Season 1/2/3 the same way.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CAND = json.loads((ROOT / '_private/pb-candidate.json').read_text(encoding='utf8'))
S3 = json.loads((ROOT / '_private/pb-s3.json').read_text(encoding='utf8'))
OLD = json.loads((ROOT / 'data/pokebonk-tools-reference.json').read_text(encoding='utf8'))

# The client interpolates the localized type name into otherwise English item text.
ES_TYPES = {'Fuego': 'Fire', 'Agua': 'Water', 'Planta': 'Grass', 'Eléctrico': 'Electric', 'Hielo': 'Ice',
            'Lucha': 'Fighting', 'Veneno': 'Poison', 'Tierra': 'Ground', 'Volador': 'Flying', 'Psíquico': 'Psychic',
            'Bicho': 'Bug', 'Roca': 'Rock', 'Fantasma': 'Ghost', 'Dragón': 'Dragon', 'Siniestro': 'Dark',
            'Acero': 'Steel', 'Hada': 'Fairy'}


def english(text):
    return re.sub(r'\b(' + '|'.join(ES_TYPES) + r')(?=-type)', lambda m: ES_TYPES[m[1]], text)


def build():
    species = {x['id']: x for x in S3['species']}
    moves = S3['moves']
    passives = S3['passives']
    league = []
    for m in CAND['league']:
        sp = species[m['id']]
        kit = []
        for key in m['kit']:
            mv = moves[key]
            kit.append({'key': key, 'name': mv['name'], 'type': mv['type'], 'cls': mv['cls'],
                        'runtime': {'cls': mv['cls'], 'arch': mv['arch'], 'dmg': mv['dmg'], 'cd': mv['cd'],
                                    'count': mv['count'], 'area': mv['area'], 'status': mv['status']}})
        p = passives[m['passive']]
        league.append({'id': m['id'], 'name': sp['name'], 'types': sp['types'], 'role': m['role'],
                       'rank': m['rank'], 'start': bool(m.get('start')),
                       'passive': {'key': m['passive'], 'name': p['name'], 'desc': p['desc'], 'mods': p['mods']},
                       'kit': kit, 'challenge': m['challenge'],
                       'region': 'kanto' if m['id'] <= 151 else 'johto'})
    items = [{**i, 'desc': english(i['desc'])} for i in CAND['items']]
    data = {'version': S3['observed']['version'], 'build': S3['observed']['build'], 'season': 3,
            'checked': '2026-11-13', 'source_client': S3['menus'],
            'league': league, 'fusions': S3['fusions'], 'items': items,
            'vitamins': OLD['vitamins'], 'lab': CAND['lab']}
    (ROOT / 'data/pokebonk-s3-reference.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf8')
    return data


if __name__ == '__main__':
    d = build()
    print(d['version'], len(d['league']), 'league,', len(d['fusions']), 'fusions,', len(d['items']), 'items')
