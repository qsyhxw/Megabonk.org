"""Compact catalog thumbs from existing reviewed game images; no remote fetch."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for game in json.loads((ROOT/'data/game-sections.json').read_text(encoding='utf8')):
 im=Image.open(ROOT/game['original_image'].lstrip('/')).convert('RGB')
 for w in game['sizes']:
  assert w<=im.width,game['id']+' must not upscale'
  f=ROOT/(game['image'].lstrip('/')+'-'+str(w)+'.webp');f.parent.mkdir(exist_ok=True)
  im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS).save(f,quality=82)
print('Built compact game-discovery thumbnails from reviewed local sources.')
