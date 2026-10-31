"""Shared screenshot links between playable sections; no remote requests or scripts."""
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
GAMES = json.loads((ROOT / 'data/play-games.json').read_text(encoding='utf-8'))

def recommendations(current):
    cards = []
    for game in GAMES:
        if game['id'] == current:
            continue
        e = {k: escape(str(v), quote=True) for k, v in game.items()}
        cards.append(f'''<article class="play-rec-card"><a class="play-rec-link" href="{e['url']}"><img src="{e['image']}-800.webp" srcset="{e['image']}-800.webp 800w, {e['image']}-1280.webp 1280w" sizes="(max-width: 600px) calc(100vw - 36px), 480px" width="1280" height="800" loading="lazy" alt="{e['alt']}"><div><h3>{e['name']}</h3><p>{e['summary']}</p><span class="play-rec-action">Play {e['name']} <span aria-hidden="true">→</span></span></div></a><p class="play-rec-caption">{e['caption']} <a href="{e['source']}" target="_blank" rel="noopener noreferrer">{e['host']} ↗</a></p></article>''')
    return '<section class="play-recommendations" id="more-games" aria-labelledby="more-games-heading" data-play-background><div class="play-rec-heading"><p>YOUR NEXT RUN</p><h2 id="more-games-heading">More games to play</h2><p>Try another survivor game, right here on Megabonk.org.</p></div><div class="play-rec-grid">' + ''.join(cards) + '</div></section>'

def stylesheet(html):
    return html.replace('</head>', '<link rel="stylesheet" href="/assets/play-recommendations.css"></head>', 1)
