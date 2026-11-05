"""Rebuild original-menu captures and native game portraits without upscaling.

Original sources: pokedive.com/en/ captured 5 Nov 2026, and
https://pokedive.com/assets/pokemon/0253s/portrait.png (shiny Grovyle),
https://pokedive.com/assets/pokemon/0253/portrait.png (normal Grovyle).
The two portraits are original 40px assets, not a fabricated game screenshot.
"""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT/'assets/pokedive/source').glob('*.png'):
 im=Image.open(p)
 widths=[800,min(1280,im.width)] if im.width>=800 else [im.width]
 for w in sorted(set(widths)):
  im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS).save(p.parent.parent/f'{p.stem}-{w}.webp',quality=90)
print('Built original-menu and native 40px portrait WebPs; no upscaling.')
