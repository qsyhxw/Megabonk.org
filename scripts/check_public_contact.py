"""Block retired public contact addresses in deployable pages and generators."""
from pathlib import Path
import json
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))
    email = config['email']
    assert email == 'contact@megabonk.org', 'Review approved site contact before changing it'
    retired = config['retired_public_emails']
    files = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT
    ).decode('utf8').splitlines()
    targets = sorted({name for name in files if Path(name).suffix.lower() in {'.html', '.htm'}
                      or (name.startswith('scripts/build_') and name.endswith('.py'))})
    errors = []
    for name in targets:
        text = unquote((ROOT / name).read_text(encoding='utf-8-sig')).lower()
        for address in retired:
            if address.lower() in text:
                errors.append(f'{name}: retired public email {address}')
    for name in ['contact/index.html', 'pokelit/index.html']:
        text = (ROOT / name).read_text(encoding='utf8')
        if email not in text or 'mailto:' + email not in text:
            errors.append(f'{name}: missing configured public contact')
    for error in errors:
        print('FAIL', error)
    print(f'{"FAIL" if errors else "PASS"}: public contact in {len(targets)} pages/generators')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
