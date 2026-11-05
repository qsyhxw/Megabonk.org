"""Shared screenshot links between playable sections; no remote requests or scripts."""
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
GAMES = json.loads((ROOT / 'data/play-games.json').read_text(encoding='utf-8'))

def recommendations(current, lang='en'):
    locale = {}
    if lang != 'en':
        locale = json.loads((ROOT / 'data/play-games-locales.json').read_text(encoding='utf-8'))[lang]
    cards = []
    for game in GAMES:
        if game['id'] == current:
            continue
        if locale:
            game = {**game, **locale['games'][game['id']]}
        e = {k: escape(str(v), quote=True) for k, v in game.items()}
        action = escape(game.get('action', 'Play ' + game['name']))
        cards.append(f'''<article class="play-rec-card"><a class="play-rec-link" href="{e['url']}"><img src="{e['image']}-800.webp" srcset="{e['image']}-800.webp 800w, {e['image']}-1280.webp 1280w" sizes="(max-width: 600px) calc(100vw - 36px), 480px" width="{e.get('width', '1280')}" height="{e.get('height', '800')}" loading="lazy" alt="{e['alt']}"><div><h3>{e['name']}</h3><p>{e['summary']}</p><span class="play-rec-action">{action} <span aria-hidden="true">→</span></span></div></a><p class="play-rec-caption">{e['caption']} <a href="{e['source']}" target="_blank" rel="noopener noreferrer">{e['host']} ↗</a></p></article>''')
    heading = locale.get('heading', ['YOUR NEXT GAME','More games to play','Choose another browser game on Megabonk.org. Each card identifies its host and gameplay.'])
    return '<section class="play-recommendations" id="more-games" aria-labelledby="more-games-heading" data-play-background><div class="play-rec-heading"><p>'+escape(heading[0])+'</p><h2 id="more-games-heading">'+escape(heading[1])+'</h2><p>'+escape(heading[2])+'</p></div><div class="play-rec-grid">' + ''.join(cards) + '</div></section>'

def stylesheet(html):
    return html.replace('</head>', '<link rel="stylesheet" href="/assets/play-recommendations.css"></head>', 1)
