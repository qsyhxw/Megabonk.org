"""Derive one concrete starting loadout per PokeBonk partner from game data (v3.20, 08 F2).

Inputs: data/pokebonk-tools-reference.json (kits, fusions, items, vitamins; client-derived)
        data/pokebonk-consensus-tier.json (tier from three public lists)
Output: data/pokebonk-loadouts.json

Rules are deterministic and documented here, not on the page:
- moves: the partner's League kit in unlock order; the signature fusion pair is marked.
- damage class: the class of the majority of kit damage (special/physical).
- items: the type booster for the partner's main move type, the class item
  (Wise Glasses / Muscle Band), and one survival item chosen from the passive.
- vitamins: Calcium for special, Protein for physical, then HP Up when the passive
  is not already defensive.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
# Season 3 reference when present (v0.9.x); Season 2 file kept for history.
_S3 = ROOT / 'data/pokebonk-s3-reference.json'
REF = json.loads((_S3 if _S3.exists() else ROOT / 'data/pokebonk-tools-reference.json').read_text(encoding='utf8'))
_SPECIES = ROOT / '_private/pb-s3.json'
SPECIES = {x['id']: x for x in json.loads(_SPECIES.read_text(encoding='utf8'))['species']} if _SPECIES.exists() else {}


def evolution_line(member):
    if member.get('evolution'):
        return [{'name': ', '.join(e['names']), 'level': e['level']} for e in member['evolution']]
    line, cur = [], member['id']
    while True:
        kids = [x for x in SPECIES.values() if x.get('evoFrom') == cur]
        if not kids:
            return line
        kid = kids[0]
        line.append({'name': kid['name'], 'level': kid.get('evoLevel')})
        cur = kid['id']
TIER = json.loads((ROOT / 'data/pokebonk-consensus-tier.json').read_text(encoding='utf8'))

ITEMS = {i['key']: i for i in REF['items']}
TYPE_ITEM = {t.split(':')[1]: i['key'] for i in REF['items'] for t in i.get('tags', []) if t.startswith('type:') and i['rarity'] == 0}
CLASS_ITEM = {'special': 'wise-glasses', 'physical': 'muscle-band'}
VITAMIN = {'special': 'calcium', 'physical': 'protein'}
DEFENSIVE = ('armor', 'shield', 'regen', 'heal', 'hp', 'damage reduction', 'evasion', 'immune')


def title(key):
    words = {'hp': 'HP', 'pp': 'PP'}
    return ' '.join(words.get(w, w.capitalize()) for w in key.split('-'))


def survival_item(passive_desc):
    d = passive_desc.lower()
    if 'heal' in d or 'regen' in d:
        return 'big-root'        # amplifies the healing the passive already has
    if 'armor' in d or 'shield' in d:
        return 'assault-vest'    # stacks with the defensive passive
    return 'leftovers'           # flat regen for partners with no sustain


def loadout(member):
    kit = member['kit']
    dmg = {}
    for move in kit:
        if move['cls'] not in CLASS_ITEM:
            continue  # status moves deal no direct damage
        rt = move.get('runtime') or {}
        dmg[move['cls']] = dmg.get(move['cls'], 0) + (rt.get('dmg', 0) / max(rt.get('cd', 1), 0.1))
    cls = max(dmg, key=dmg.get) if dmg else 'special'
    types = {}
    for move in kit:
        if move['cls'] == cls:
            types[move['type']] = types.get(move['type'], 0) + 1
    main_type = max(types, key=types.get) if types else member['types'][0]
    fusion = next((f for f in REF['fusions'] if f.get('member') == member['id'] and f.get('kind') == 'signature'), None)
    pair = set(fusion['moves']) if fusion else set()
    passive = member['passive']['desc']
    items = [TYPE_ITEM.get(main_type), CLASS_ITEM[cls], survival_item(passive)]
    vit = [VITAMIN[cls]]
    if not any(w in passive.lower() for w in DEFENSIVE):
        vit.append('hp-up')
    return {
        'id': member['id'], 'name': member['name'], 'types': member['types'], 'role': member['role'],
        'passive': {'name': member['passive']['name'], 'desc': passive},
        'class': cls, 'main_type': main_type,
        'moves': [{'key': m['key'], 'name': m['name'], 'type': m['type'], 'cls': m['cls'],
                   'fusion': m['key'] in pair} for m in kit],
        'fusion': {'name': fusion['name'], 'moves': [title(k) for k in fusion['moves']]} if fusion else None,
        'items': [{'key': k, 'name': title(k), 'desc': ITEMS[k]['desc']} for k in items if k in ITEMS],
        'vitamins': [title(v) for v in vit],
        'evolution': evolution_line(member),
        'region': member.get('region', 'kanto'),
    }


def build():
    tiers = {r['name']: r for r in TIER['rows']}
    out = []
    for member in REF['league']:
        row = tiers.get(member['name'])
        if not row or row['tier'] not in ('S', 'A'):
            continue
        item = loadout(member)
        item['tier'] = row['tier']
        item['score'] = row['score']
        out.append(item)
    out.sort(key=lambda x: ('SA'.index(x['tier']), -x['score'], x['name']))
    data = {'version': REF['version'], 'checked': REF['checked'], 'tier_version': TIER['version'], 'loadouts': out}
    (ROOT / 'data/pokebonk-loadouts.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf8')
    return data


if __name__ == '__main__':
    d = build()
    print(len(d['loadouts']), 'loadouts')
