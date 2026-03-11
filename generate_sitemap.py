import os
import xml.etree.ElementTree as ET
from datetime import datetime

base_dir = r'd:\Antigravity\Megabonk.org'
base_url = 'https://megabonk.org'

urls = []
for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, base_dir).replace('\\', '/')
            if rel_path == 'index.html':
                 url = base_url + '/'
            else:
                 url = base_url + '/' + rel_path.replace('index.html', '')
            
            # get file modification time
            mtime = os.path.getmtime(filepath)
            lastmod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
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
print(f'Generated sitemap.xml with {len(urls)} URLs.')
