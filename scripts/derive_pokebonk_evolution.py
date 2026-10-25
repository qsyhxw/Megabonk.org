"""Derive the small reviewed run-level example table from numeric inputs."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def derive(data):
    species = {r['id']: r for r in data['species']}
    children = {}
    for r in species.values():
        if r['evoFrom'] is not None:
            children.setdefault(r['evoFrom'], []).append(r)
    examples = []
    for entry in data['league_examples']:
        start = entry['id']
        current, floor, stage = start, 1, 0
        route = []
        if entry.get('branch'):
            names = ', '.join(species[n]['name'] for n in entry['branch'])
            route.append(f"Choose {names} at level {entry['evoLevel']}")
            reason = 'League branch choice, not a random branch instruction.'
        else:
            while children.get(current):
                following = children[current][0]
                raw = following['evoLevel']
                if raw is None:
                    raw = 20 if species[current]['evoStage'] == 0 else 34
                threshold = min(30, max(16, math.floor(8 + raw + .5))) if children.get(following['id']) else min(50, max(36, math.floor(22 + raw * .6 + .5)))
                if current == start and entry.get('evoLevel'):
                    threshold = entry['evoLevel']
                if 'evoLevels' in entry and stage < len(entry['evoLevels']):
                    threshold = entry['evoLevels'][stage]
                threshold = max(threshold, floor)
                route.append(f"{following['name']} at level {threshold}")
                current, floor, stage = following['id'], threshold + 3, stage + 1
            reason = 'League override takes priority.' if 'evoLevels' in entry or 'evoLevel' in entry else 'Runtime transform of the next species’ raw level.'
        examples.append({'starter': species[start]['name'], 'route': ' → '.join(route), 'reason': reason})
    return {'version': data['version'], 'build': data['build'], 'checked': data['checked'], 'sources': data['sources'], 'method': 'Client runEvolution transform, League overrides, and the three-level post-evolution minimum; no gameplay claim.', 'examples': examples}


if __name__ == '__main__':
    data = json.loads((ROOT/'data/pokebonk-evolution-inputs.json').read_text(encoding='utf-8'))
    (ROOT/'data/pokebonk-evolution.json').write_text(json.dumps(derive(data), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
