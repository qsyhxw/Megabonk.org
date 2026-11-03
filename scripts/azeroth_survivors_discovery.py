"""Small task-entry improvements; no new gameplay or current-version claims."""
from azeroth_survivors_content import P, a, para


def improve_pages(pages):
    for page in pages:
        if page['slug'] == 'beginners-guide/':
            for index, (key, title, body) in enumerate(page['parts']):
                if key == 'start':
                    body = para('Need a route into the game? ' + a('play/#edition', 'Check the third-party edition')
                                + ' or ' + a('download-platforms/#download', 'find the original Windows download')
                                + '. The steps below describe the original host; check the edition before following them.') + body
                if key == 'launch-checks':
                    body = para('If the game has not reached the hero picker, '
                                + a('troubleshooting/#gpu-check', 'check WebGPU and adapter availability')
                                + ' or ' + a('troubleshooting/#triage', 'match the message you see')
                                + '. The browser check does not test the game server. Keep your existing save before changing host or clearing storage.') + body
                page['parts'][index] = (key, title, body)
        if page['slug'] == 'best-class/':
            # Put the existing comparison before the longer optional questionnaire.
            order = ['choose', 'current-comparison', 'progress', 'finder', 'method']
            page['parts'].sort(key=lambda part: order.index(part[0]))
    return pages


def improve_home(html):
    old = ('<div class="actions"><a class="button" href="' + P + 'play/">Play in a game window →</a>')
    html = html.replace(old, '<div class="actions">', 1)
    needle = '<a class="button secondary" href="' + P + 'beginners-guide/">Plan your first run →</a>'
    html = html.replace(needle, '<a class="button secondary" href="' + P + 'play/">Play a third-party version →</a>'
                        + '<a class="button secondary" href="' + P + 'beginners-guide/">How to play: first-run guide →</a>', 1)
    html = html.replace('Opens wow.aethus.pl in a new tab. The original blocks embedded play; your game and save stay on its host.',
                        'The original opens wow.aethus.pl in a new tab. The game window uses a separate third-party provider; version and save compatibility need verification. Keep progress with the host that created it.', 1)
    html = html.replace(a('mobile/', 'Phone and tablet checks') + ' · ' + a('save-backup/', 'Export before switching'),
                        a('download-platforms/#download', 'Windows download: source and setup') + ' · '
                        + a('mobile/', 'Phone and tablet checks') + ' · ' + a('save-backup/', 'Export before switching'), 1)
    html = html.replace(a('troubleshooting/', 'Fix loading or WebGPU') + ' · ',
                        a('beginners-guide/', 'How to play: controls and first run') + ' · '
                        + a('troubleshooting/', 'Fix loading or WebGPU') + ' · ', 1)
    return html
