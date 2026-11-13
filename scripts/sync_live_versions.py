#!/usr/bin/env python3
"""AUTO_SYNC of whitelisted version labels (SOP 05 §2.9; contract in SITE_PROFILE).

  python scripts/sync_live_versions.py [--dry-run] [--offline FIXTURE.json]

Writes only: data/live-versions.json, the text inside data-live / data-live-date
spans on each entry's pages, data/content-dates.json and the sitemap <lastmod>
of those pages. Any rejected entry (bad format, older version, major-version
jump, missing span, fetch failure) stops the whole run before writing.
"""
import argparse, json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from live_versions import DATA, long_date

ROOT = Path(__file__).resolve().parents[1]
UA = 'megabonk-version-sync/1.0 (+https://megabonk.org)'
FORMATS = {
    'spires-desktop': r'v\d+\.\d+\.\d+',
    'spires-browser': r'\d{8}[a-z]?',
    'midgard-client': r'\d+\.\d+\.\d+',
    'mythic-ios': r'\d+\.\d+\.\d+',
}


class Reject(Exception):
    pass


def get(url, raw=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode('utf8')
    return body if raw else json.loads(body)


def fetch(key):
    """(version, release date ISO or None) from the entry's own source only."""
    if key == 'spires-desktop':
        g = get('https://api.github.com/repos/Chrisl252/spiresofazeroth/releases/latest')
        if g.get('draft') or g.get('prerelease'):
            raise Reject('latest release is draft/prerelease')
        return g['tag_name'], g['published_at'][:10]
    if key == 'spires-browser':
        m = re.search(r'BUILD\s*=\s*"([^"]+)"', get('https://thewowdb.com/spiresofazeroth/js/version.js', raw=True))
        if not m:
            raise Reject('BUILD constant not found in version.js')
        return m.group(1), None
    if key == 'midgard-client':
        m = get('https://raw.githubusercontent.com/Gon-Analista/midgard-survivors-updates/main/manifest.json')
        return (m.get('patch') or {}).get('version') or m['base'], None
    if key == 'mythic-ios':
        res = get('https://itunes.apple.com/lookup?id=6775568333&country=us')['results']
        if len(res) != 1 or res[0].get('trackId') != 6775568333:
            raise Reject('App Store lookup did not return exactly the Pixery app')
        return res[0]['version'], res[0]['currentVersionReleaseDate'][:10]
    raise Reject('no source adapter')


def parts(v):
    return [int(x) for x in re.findall(r'\d+', v)] + re.findall(r'[a-z]+$', v)


def check(key, old, new):
    if not re.fullmatch(FORMATS[key], new or ''):
        raise Reject(f'unexpected format {new!r}')
    if parts(new) < parts(old):
        raise Reject(f'version went backwards {old} -> {new}')
    if key != 'spires-browser' and parts(new)[0] != parts(old)[0]:
        raise Reject(f'major version jump {old} -> {new}; needs review')


def read_raw(path):
    with open(path, encoding='utf8', newline='') as f:
        return f.read()


def apply_spans(text, path, key, version, when):
    out, n1 = re.subn(rf'(<strong data-live="{key}">)[^<]*(</strong>)', rf'\g<1>{version}\g<2>', text)
    out, n2 = re.subn(rf'(<span data-live-date="{key}">)[^<]*(</span>)', rf'\g<1>{long_date(when)}\g<2>', out)
    if n1 != 1 or n2 != 1:
        raise Reject(f'{path}: expected one value and one date span for {key}, found {n1}/{n2}')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--offline', help='fixture JSON {key: [version, date|null]} instead of fetching')
    a = ap.parse_args()
    data = json.loads(DATA.read_text(encoding='utf8'))
    fixture = json.loads(Path(a.offline).read_text(encoding='utf8')) if a.offline else None
    today = datetime.now(timezone.utc).date().isoformat()

    changed, errors = [], []
    for key, entry in data.items():
        try:
            version, released = fixture[key] if fixture else fetch(key)
            check(key, entry['value'], version)
        except Exception as e:
            errors.append(f'{key}: {e}')
            continue
        entry['checked'] = today
        if version != entry['value']:
            entry.update(value=version, date=released or today)
            changed.append(key)
            print(f'{key}: -> {version} ({entry["date"]})')

    pages = {}
    for key in changed:
        for route in data[key]['pages']:
            path = ROOT / route.strip('/') / 'index.html'
            try:
                text = pages.get(path) or read_raw(path)
                pages[path] = apply_spans(text, path, key, data[key]['value'], data[key]['date'])
            except (OSError, Reject) as e:
                errors.append(str(e))

    if errors:
        print('REJECTED, nothing written:\n- ' + '\n- '.join(errors), file=sys.stderr)
        return 1
    if not changed:
        print('No version changes.')
    if a.dry_run:
        return 0
    if not changed:
        return 0  # checked dates alone are not worth a commit

    for path, text in pages.items():
        path.write_text(text, encoding='utf8', newline='')
    DATA.write_text(json.dumps(data, indent=2) + '\n', encoding='utf8', newline='\n')

    urls = sorted({'https://megabonk.org' + r for k in changed for r in data[k]['pages']})
    dates_path = ROOT / 'data' / 'content-dates.json'
    dates = json.loads(dates_path.read_text(encoding='utf8'))
    for url in urls:
        dates[url] = today
    dates_path.write_text(json.dumps(dates, indent=2, ensure_ascii=False).replace('\n', '\r\n') + '\r\n',
                          encoding='utf8', newline='')
    sitemap = ROOT / 'sitemap.xml'
    xml = read_raw(sitemap)
    for url in urls:
        xml, n = re.subn(rf'(<loc>{re.escape(url)}</loc>\s*<lastmod>)[^<]+', rf'\g<1>{today}', xml)
        if n != 1:
            print(f'warning: {url} found {n} times in sitemap.xml', file=sys.stderr)
    sitemap.write_text(xml, encoding='utf8', newline='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
