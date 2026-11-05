"""Rebuild responsive images from committed originals; never upscale captures.

demo-characters/combat: actual original itch.io v0.2.4 Demo, 5 Nov 2026.
coop-controls: https://poncle.games/assets/controller-keyboard-coop-faq.png
All game artwork belongs to poncle. Raw capture seeds are versioned so builds
do not depend on private working files or silently changing remote assets.
"""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for source in (ROOT/'assets/vampire-survivors/source').glob('*.png'):
 im=Image.open(source)
 for width in [800,im.width]:
  assert width<=im.width
  im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS).save(source.parent.parent/f'{source.stem}-{width}.webp',quality=88)
print('Built six responsive WebPs from three original game images; no upscaling.')
