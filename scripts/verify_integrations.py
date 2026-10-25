"""Check every deployable HTML/HTM file against the reviewed integration map.

The repository is the existing Cloudflare Pages source. Git-excluded research
files are not deployed; a temporary HTML-only mirror lets the shared detector
scan all public documents without reading private browser captures.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import check_integrations as guard

ROOT = Path(__file__).resolve().parents[1]


def containers(document):
    return [{'tag': n['tag'], 'attrs': n['attrs'], 'location': n['location']}
            for n in document.nodes if n['tag'] in ('ins', 'iframe') or
            (n['tag'] == 'div' and n['attrs'].get('id', '').startswith('container-'))]


def public_html():
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode('utf-8').splitlines()
    return sorted({p for p in paths if Path(p).suffix.lower() in ('.html', '.htm')})


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--baseline', type=Path)
    group.add_argument('--first-inventory', action='store_true')
    parser.add_argument('--change-note')
    args = parser.parse_args()
    config = json.loads((ROOT/'config/integrations.json').read_text(encoding='utf-8'))
    guard.validate(config)
    if args.baseline:
        before = json.loads(args.baseline.read_text(encoding='utf-8'))
        guard.validate(before)
        if before != config and not args.change_note:
            raise SystemExit('FAIL: configuration changed without a reviewed ROADMAP reference')
    else:
        print('FIRST_INVENTORY: no previous reviewed configuration existed')
    files = public_html()
    with tempfile.TemporaryDirectory(prefix='megabonk-integration-') as temp:
        out = Path(temp)
        for file in files:
            dest = out/file
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/file, dest)
        errors, count = guard.check(out, config)
        # Original containers were captured from the preserved pre-change Git
        # revision, independently of the edited HTML. New slots need review.
        for file in files:
            document = guard.Document()
            document.feed((out/file).read_text(encoding='utf-8-sig'))
            if containers(document) != config.get('protected_containers', {}).get(file, []):
                errors.append(file + ': integration container markup differs from reviewed inventory')
    for error in errors:
        print('FAIL:', error)
    print(f'{"STATIC_PASS" if not errors else "STATIC_FAILED"}: {count} public HTML/HTM files; exact scripts, IDs, counts and locations checked')
    if args.change_note:
        print('CONFIG_CHANGE_REFERENCE:', args.change_note)
    print('Runtime, CSP, Privacy and backend are separate checks; this command does not generate new expectations.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
