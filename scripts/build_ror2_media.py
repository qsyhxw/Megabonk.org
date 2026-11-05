"""Recreate responsive WebPs from reviewed official game-image seeds.

Seeds © Hopoo Games / Gearbox. Source frames from the official Steam 1.0
Wide trailer 256795993 (38s co-op; 44.8s Reliquary), not cover images.
Beacons: official Steam v1.3.4 patch note, 10 Sep 2024; OLD/NEW preserved.
No remote fetch or image upscaling during builds.
"""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for f in (ROOT/'assets/risk-of-rain-2/source').glob('*.png'):
 im=Image.open(f).convert('RGB')
 for w in sorted(set([min(800,im.width),min(1280,im.width)])):
  im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS).save(f.parent.parent/f'{f.stem}-{w}.webp',quality=88)
 print(f.stem,im.size)
