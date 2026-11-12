"""Task-specific Midgard layouts, preserving reviewed article facts and site services."""
from bs4 import BeautifulSoup


def adapt(html, slug):
    start = html.index('<main ')
    end = html.index('</main>', start) + len('</main>')
    soup = BeautifulSoup(html[start:end], 'html.parser')
    main = soup.main
    if not slug:
        intro = main.select_one('.article-head')
        intro['class'] = ['home-intro']
        copy = soup.new_tag('div', attrs={'class': 'hero-copy'})
        for node in list(intro.contents):
            copy.append(node.extract())
        intro.append(copy)
        photo = main.select_one('figure').extract()
        photo.img.attrs.pop('loading', None)
        photo.img['fetchpriority'] = 'high'
        photo['class'] = ['game-image', 'hero-image']
        intro.append(photo)
        actions = BeautifulSoup('<div class="hero-actions"><a class="primary-action" href="#download">Choose your download</a><a href="#guides">Find a guide ↓</a></div>', 'html.parser')
        copy.append(actions)
        main.select_one('.toc').decompose()
        guides = main.select_one('#guides')
        guides.clear()
        guides.append(BeautifulSoup('''<div class="guide-groups"><section><h2>Get the game running</h2><a class="task-link" href="/midgard-survivors/android/"><strong>Android</strong><span>Vulkan, OpenGL and launch problems</span><b aria-hidden="true">→</b></a><a class="task-link" href="/midgard-survivors/mac/"><strong>Mac</strong><span>Alpha installation and the damaged-app message</span><b aria-hidden="true">→</b></a></section><section><h2>Plan your next run</h2><a class="task-link" href="/midgard-survivors/equipment/"><strong>Equipment</strong><span>Keep items, equip gear and review upgrades</span><b aria-hidden="true">→</b></a><a class="task-link" href="/midgard-survivors/co-op/"><strong>Co-op</strong><span>Rooms, accounts and progression boundaries</span><b aria-hidden="true">→</b></a></section></div>''', 'html.parser'))
        intro.insert_after(guides.extract())
        main.select_one('#next').decompose()
        main.select_one('#download')['class'] = ['download-section']
    else:
        intro = main.select_one('.article-head')
        crumb = soup.new_tag('a', href='/midgard-survivors/', attrs={'class': 'back-link'})
        crumb.string = '← Midgard Survivors guides'
        intro.insert(0, crumb)
        # The Mac command gets a distinct treatment, while Android keeps its symptom table.
        if slug == 'mac/':
            main.select_one('#damaged')['class'] = ['command-section']
        if slug == 'equipment/':
            main.select_one('#equip')['class'] = ['equipment-route']
    for table in main.select('table'):
        headings = [th.get_text(' ', strip=True) for th in table.select('thead th')]
        for row in table.select('tbody tr'):
            for cell, heading in zip(row.select('td'), headings):
                cell['data-label'] = heading
    result = html[:start] + str(main) + html[end:]
    kind = 'midgard-home' if not slug else 'midgard-article task-' + slug.strip('/')
    return result.replace('guide-layout midgard-guide', 'guide-layout midgard-guide ' + kind)
