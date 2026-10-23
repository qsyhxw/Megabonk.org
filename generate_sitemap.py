import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime

base_dir = os.path.dirname(os.path.abspath(__file__))
base_url = 'https://megabonk.org'

urls = []
excluded_files = {
    '404.html',
    'ceshi.html',
    'yandex_079a4f31aab726cf.html',
    'guides/characters/character-tier-list-2025.html',
    'guides/builds/gigachad-best-build/index.html',
    'guides/builds/knight-best-build/index.html',
    'guides/builds/skeleton-best-build/index.html',
    'faq/is-megabonk-on-console.html',
}

excluded_prefixes = ('components/', '_private/', 'outputs/', 'PAGE_REPORTS/', '.git/', 'tests/')

# A checkout timestamp is not a content update. Keep published dates unless a
# page has an explicit reviewed update in the section's content-date manifest.
prior_dates = {}
try:
    for prior_url in ET.parse(os.path.join(base_dir, 'sitemap.xml')).getroot():
        prior_dates[prior_url.findtext('{*}loc')] = prior_url.findtext('{*}lastmod')
except (OSError, ET.ParseError):
    pass
content_dates = {}
date_manifest = os.path.join(base_dir, 'data', 'content-dates.json')
if os.path.exists(date_manifest):
    with open(date_manifest, encoding='utf-8') as date_file:
        content_dates = json.load(date_file)
def public_path(rel_path):
    """Return the canonical Cloudflare Pages route for a physical HTML file."""
    if rel_path == 'index.html':
        return '/'
    if rel_path.endswith('/index.html'):
        return '/' + rel_path[:-len('index.html')]
    return '/' + rel_path[:-len('.html')]


for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'_private', 'outputs', 'PAGE_REPORTS', 'tests', 'node_modules'}]
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, base_dir).replace('\\', '/')
            if rel_path in excluded_files or rel_path.startswith(excluded_prefixes):
                continue
            with open(filepath, encoding='utf-8', errors='ignore') as page_file:
                page_source = page_file.read()
            if re.search(
                r'<meta[^>]+name=["'']robots["''][^>]+content=["''][^"'']*noindex',
                page_source,
                re.IGNORECASE,
            ):
                continue
            url = base_url + public_path(rel_path)
            canonical_match = re.search(
                r'<link[^>]+rel=["'']canonical["''][^>]+href=["'']([^"'']+)["'']',
                page_source,
                re.IGNORECASE,
            )
            if canonical_match and canonical_match.group(1) != url:
                continue

            # get file modification time
            mtime = os.path.getmtime(filepath)
            lastmod = content_dates.get(url) or prior_dates.get(url) or datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            urls.append((url, lastmod))

# remove duplicates and construct XML
urls = list(set(urls))
urls.sort()

urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

for url, lastmod in urls:
    url_elem = ET.SubElement(urlset, 'url')
    loc = ET.SubElement(url_elem, 'loc')
    loc.text = url
    lastmod_elem = ET.SubElement(url_elem, 'lastmod')
    lastmod_elem.text = lastmod
    changefreq = ET.SubElement(url_elem, 'changefreq')
    changefreq.text = 'weekly'

tree = ET.ElementTree(urlset)
ET.indent(tree, space='  ', level=0)
tree.write(os.path.join(base_dir, 'sitemap.xml'), encoding='utf-8', xml_declaration=True)
with open(os.path.join(base_dir, 'sitemap.xml'), 'a', encoding='utf-8') as sitemap_file:
    sitemap_file.write('\n')
with open(os.path.join(base_dir, 'pages_list.txt'), 'w', encoding='utf-8', newline='') as pages_file:
    pages_file.write(chr(10).join(url for url, _ in urls) + chr(10))
print(f'Generated sitemap.xml and pages_list.txt with {len(urls)} URLs.')
