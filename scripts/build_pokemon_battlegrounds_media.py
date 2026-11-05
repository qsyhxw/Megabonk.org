"""Responsive original-host UI captures, 2026-11-05. No enlargement or game copy.

Game artwork © respective owners; PB Ranked by Sondre Norheim.
Login capture illustrates the real sign-in task, not an authenticated match.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
for source in (ROOT / 'assets/pokemon-battlegrounds/source').glob('*.png'):
    image = Image.open(source)
    for width in ([480, 640] if image.width == 640 else [800, 1280]):
        assert width <= image.width
        image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS).save(source.parent.parent / f'{source.stem}-{width}.webp', quality=88)
print('Built responsive PB Ranked captures from versioned original UI screenshots.')
