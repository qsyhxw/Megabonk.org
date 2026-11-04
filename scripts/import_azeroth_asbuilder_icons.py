"""Reproduce reviewed 64px reference icons from the pinned public ASBuilder atlas."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprite', type=Path, help='Use a previously downloaded source atlas')
    args = parser.parse_args()
    data = json.loads((ROOT / 'data/azeroth-asbuilder-icons.json').read_text(encoding='utf8'))
    raw = args.sprite.read_bytes() if args.sprite else urlopen(data['sprite'], timeout=45).read()
    if sha256(raw).hexdigest() != data['sprite_sha256']:
        raise ValueError('The source atlas changed. Review its image mappings before importing.')
    image = Image.open(BytesIO(raw))
    if image.size != (1280, 1088):
        raise ValueError('Unexpected source atlas dimensions')
    assets = {entry['asset']: entry['crop'] for entry in data['entities']}
    for asset, (x, y) in assets.items():
        target = ROOT / asset.lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        image.crop((x, y, x + data['size'], y + data['size'])).save(target, lossless=True)
    print(f'Wrote {len(assets)} reviewed reference images. Source and artwork credits remain in the manifest.')


if __name__ == '__main__':
    main()
