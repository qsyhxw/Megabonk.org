"""Audit AdSense on tracked, directly served HTML documents; optionally repair."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = 'ca-pub-8830315294299920'
URL = f'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER}'
CODE = f'<script async src="{URL}" crossorigin="anonymous"></script>'
SCRIPT = re.compile(r'<script\b(?P<attrs>[^>]*)>\s*</script\s*>', re.I)
SRC = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.I)
TRUST = re.compile(r'(^|/)(?:about|about-us|contact|contact-us|privacy|privacy-policy|terms|terms-of-service|cookie-policy|404)(?:[/.]|$)', re.I)

def loaders(source):
    found = []
    for m in SCRIPT.finditer(source):
        src = SRC.search(m['attrs'])
        if src and urlsplit(src[1]).hostname == 'pagead2.googlesyndication.com' and urlsplit(src[1]).path in ('/pagead/js', '/pagead/js/adsbygoogle.js'):
            found.append((m, src[1]))
    return found

def category(file, source):
    if TRUST.search(file):
        return 'EXCLUDED'
    if not re.search(r'<html\b', source, re.I) or file.startswith('components/') or re.search(r'<meta[^>]+http-equiv=["\']refresh', source, re.I) or file.startswith(('yandex_', 'google')):
        return 'NOT_CONTENT'
    return 'CONTENT'

def run(fix=False):
    rows = []
    files = subprocess.check_output(['git', 'ls-files', '*.html'], cwd=ROOT).decode('utf-8').splitlines()
    for file in files:
        p = ROOT/file
        source = p.read_bytes().decode('utf-8')
        kind = category(file, source)
        matches = loaders(source)
        before = len(matches)
        bad_urls = [src for _, src in matches if src != URL]
        new = source
        if fix and kind == 'CONTENT':
            # Keep the first valid head tag verbatim where possible, remove all
            # later loaders (including old /pagead/js URLs).
            for match, src in reversed(matches):
                replacement = ''
                if match == matches[0][0] and match.end() < source.lower().index('</head>'):
                    replacement = match[0] if src == URL and 'async' in match['attrs'] and 'crossorigin' in match['attrs'] else CODE
                new = new[:match.start()] + replacement + new[match.end():]
            if not loaders(new):
                new = re.sub(r'</head\s*>', CODE+'\n</head>', new, count=1, flags=re.I)
        elif fix and kind == 'EXCLUDED':
            for match, _ in reversed(matches):
                new = new[:match.start()] + new[match.end():]
        if fix and new != source:
            new = re.sub(r'(?m)^[\t ]+(?=\r?$)', '', new)
        if new != source:
            p.write_bytes(new.encode('utf-8'))
        actual = loaders(new)
        errors = []
        if kind == 'CONTENT':
            if len(actual) != 1 or actual[0][1] != URL:
                errors.append('expected one matching loader')
            elif actual[0][0].end() > new.lower().index('</head>'):
                errors.append('loader outside head')
        elif kind == 'EXCLUDED' and (actual or re.search(r'<ins\b[^>]*class=["\'][^"\']*adsbygoogle',new,re.I)):
            errors.append('excluded page has advertising')
        rows.append(dict(file=file,kind=kind,before=before,after=len(actual),bad_urls=bad_urls,changed=new!=source,errors=errors))
    return rows

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fix',action='store_true');parser.add_argument('--report');args=parser.parse_args()
    rows=run(args.fix)
    if args.report:
        (ROOT/args.report).write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps({'html':len(rows),'content':sum(r['kind']=='CONTENT' for r in rows),'excluded':sum(r['kind']=='EXCLUDED' for r in rows),'other':sum(r['kind']=='NOT_CONTENT' for r in rows),'changed':sum(r['changed'] for r in rows),'before_missing':sum(r['kind']=='CONTENT' and r['before']==0 for r in rows),'before_multiple':sum(r['kind']=='CONTENT' and r['before']>1 for r in rows),'before_wrong_url':sum(bool(r['bad_urls']) for r in rows),'errors':[r for r in rows if r['errors']]},indent=2))
    raise SystemExit(1 if any(r['errors'] for r in rows) else 0)
