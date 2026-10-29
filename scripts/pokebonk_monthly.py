"""Monthly search-intent handoffs; preserve existing page metadata and game data."""
def apply_monthly_handoffs(ctx):
    pages, section = ctx['PAGES'], ctx['section']
    blocks = {
      '/pokebonk/beginners-guide/': ('choose-entry', 'Looking for the game, a first run, or a build?', '<p>For the game overview and all available guides, start at the <a href="/pokebonk/">PokeBonk homepage</a>. To launch the separately hosted browser edition, open <a href="/pokebonk/play/">Play PokeBonk</a> and read its version and save notice before starting. This page covers first-run setup and controls.</p><p>Choose a partner with the <a href="/pokebonk/starters/">starter comparison</a>, then use the <a href="/pokebonk/build-planner/">build planner</a> to check a specific setup. If you searched for Pokémon Megabonk, the <a href="/pokebonk/megabonk-vs-pokebonk/">game comparison</a> explains which project these guides cover. A launch page, a beginner route and a build plan answer different tasks.</p>'),
      '/pokebonk/starters/': ('tier-or-starter', 'Starter choice or a full PokeBonk tier list?', '<p>This page helps you choose an initial partner. For a wider ranking question, use the <a href="/pokebonk/tier-list/">PokeBonk tier-list guide</a>, which explains the comparison limits; the starter selector does not establish a universal ranking.</p><p>Before comparing options, choose your goal: a first run, a specific build, or a later unlock. Use the <a href="/pokebonk/beginners-guide/">beginner route</a> for first-run setup, the <a href="/pokebonk/pokemon/">partner database</a> for the wider roster, and the <a href="/pokebonk/build-planner/">build planner</a> to compare declared moves, items and upgrades under the same conditions. Keep the goal and owned upgrades fixed when comparing partners; a different setup answers a different question.</p>')
    }
    for path, (anchor, title, text) in blocks.items():
        page = pages[path]
        marker = '<section class="sources"'
        assert marker in page['html'] and f'id="{anchor}"' not in page['html']
        page['html'] = page['html'].replace(marker, section(anchor, title, text) + marker, 1)
        page['html'] = page['html'].replace('<strong>On this page</strong>', '<strong>On this page</strong>' + f'<a href="#{anchor}">{title}</a>', 1)
