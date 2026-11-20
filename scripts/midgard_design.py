"""Task-specific Midgard layouts, preserving reviewed article facts and site services."""
from bs4 import BeautifulSoup


def adapt(html, slug):
    start = html.index('<main ')
    end = html.index('</main>', start) + len('</main>')
    soup = BeautifulSoup(html[start:end], 'html.parser')
    main = soup.main
    # Keep task actions nearby and collect supporting sources once per destination.
    sources = {}
    retained = set()
    for anchor in list(main.select('a[href^="https://"]')):
        url = anchor['href']
        section = anchor.find_parent('section')
        section_id = section.get('id') if section else ''
        action = (section_id in ['download', 'choose', 'install'] and 'nearq.itch.io' in url)
        command_source = slug == 'mac/' and section_id == 'damaged' and 'reddit.com' in url
        support = slug == 'co-op/' and section_id == 'save' and 'nearq.itch.io' in url
        if (action or command_source or support) and url not in retained:
            retained.add(url)
            continue
        label = anchor.get_text(' ', strip=True).split('↗')[0].strip()
        if url not in sources:
            sources[url] = label
        anchor.replace_with(label)
    for url in retained:
        sources.pop(url, None)
    # A listing already used for installation also supplies its comments and notes.
    if any('nearq.itch.io' in url for url in retained):
        sources = {url: label for url, label in sources.items() if 'nearq.itch.io' not in url}
    if sources:
        evidence = soup.new_tag('section', id='checks', attrs={'class': 'source-notes'})
        heading = soup.new_tag('h2')
        heading.string = 'Sources'
        evidence.append(heading)
        paragraph = soup.new_tag('p')
        for index, (url, label) in enumerate(sources.items()):
            if index:
                paragraph.append(' · ')
            anchor = soup.new_tag('a', href=url)
            anchor.string = label
            paragraph.append(anchor)
        evidence.append(paragraph)
        main.select_one('#next').insert_before(evidence)

    if not slug:
        from midgard_hub import compose
        compose(main)
    else:
        if main.select_one('#next'):
            main.select_one('#next').decompose()
        intro = main.select_one('.article-head')
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
