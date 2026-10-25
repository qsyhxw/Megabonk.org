"""Static integration regression guard. Python 3.9+, standard library only."""
import argparse
import fnmatch
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path


def applies(path, patterns):
    return any(fnmatch.fnmatchcase(path, p) or
               (p.startswith('**/') and fnmatch.fnmatchcase(path, p[3:]))
               for p in patterns)


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.section = None
        self.script = None

    def handle_starttag(self, tag, attrs):
        if tag in ('head', 'body'):
            self.section = tag
        node = {'tag': tag, 'attrs': dict(attrs), 'location': self.section, 'text': ''}
        self.nodes.append(node)
        if tag == 'script':
            self.script = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, text):
        if self.script is not None:
            self.script['text'] += text

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script = None
        if tag in ('head', 'body'):
            self.section = None


def matches(node, rule):
    if node['tag'] != rule['tag']:
        return False
    if rule.get('location') and node['location'] != rule['location']:
        return False
    if any(node['attrs'].get(k) != v for k, v in rule.get('attrs', {}).items()):
        return False
    if any(k not in node['attrs'] for k in rule.get('boolean_attrs', [])):
        return False
    if 'text_sha256' in rule:
        if node['tag'] == 'script' and not rule.get('attrs', {}).get('src') and 'src' in node['attrs']:
            return False
        digest = hashlib.sha256(node['text'].strip().encode('utf-8')).hexdigest()
        if digest != rule['text_sha256']:
            return False
    return True


def validate(config):
    if config.get('version') != 1 or config.get('reviewed') is not True:
        raise ValueError('version must be 1 and reviewed must be true after an actual inventory')
    if not isinstance(config.get('site'), str) or not config['site'].strip():
        raise ValueError('site is required')
    integrations = config.get('integrations')
    if not isinstance(integrations, list):
        raise ValueError('integrations must be a list')
    ids = set()
    for item in integrations:
        if not isinstance(item.get('id'), str) or not item['id'] or item['id'] in ids:
            raise ValueError('integration IDs must be nonempty and unique')
        ids.add(item['id'])
        if type(item.get('enabled')) is not bool:
            raise ValueError('enabled must be a boolean')
        for key in ('include', 'exclude'):
            if not isinstance(item.get(key), list) or not all(isinstance(p, str) and p for p in item[key]):
                raise ValueError(key + ' must be a list of path patterns')
        if not item['include'] or not item.get('authorization'):
            raise ValueError('include and authorization are required')
        if not isinstance(item.get('checks'), list) or not item['checks']:
            raise ValueError('each integration needs checks, including disabled integrations')
        for rule in item['checks']:
            if rule.get('tag') not in ('script', 'div', 'ins', 'iframe', 'meta', 'link'):
                raise ValueError('unsupported tag')
            if type(rule.get('count')) is not int or rule['count'] < 1:
                raise ValueError('count must be a positive integer')
            if rule.get('location') not in (None, 'head', 'body'):
                raise ValueError('location must be head or body')
            attrs = rule.get('attrs', {})
            if not isinstance(attrs, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in attrs.items()):
                raise ValueError('attrs must contain exact string values')
            if not isinstance(rule.get('boolean_attrs', []), list) or not all(isinstance(v, str) for v in rule.get('boolean_attrs', [])):
                raise ValueError('boolean_attrs must be a list of attribute names')
            digest = rule.get('text_sha256')
            if digest is not None and (not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)):
                raise ValueError('text_sha256 must be a lowercase SHA-256 digest')
            # A generic script matcher would silently approve arbitrary scripts.
            if rule['tag'] == 'script' and not attrs.get('src') and not digest:
                raise ValueError('script checks require an exact src or text_sha256')
    return integrations


def check(root, config):
    integrations = validate(config)
    errors = []
    files = sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ('.html', '.htm'))
    if not files:
        return ['no HTML files found in deployment root'], 0
    hits = {item['id']: 0 for item in integrations}
    for file in files:
        path = file.relative_to(root).as_posix()
        doc = Document()
        doc.feed(file.read_text(encoding='utf-8-sig'))
        by_tag = {}
        for node in doc.nodes:
            by_tag.setdefault(node['tag'], []).append(node)
        approved = []
        for item in integrations:
            active = item['enabled'] and applies(path, item['include']) and not applies(path, item['exclude'])
            if active:
                hits[item['id']] += 1
            for rule in item['checks']:
                # Multiple historical pages can use the same executable with
                # different counts/scopes. Inactive script rules must not
                # reject a node approved by another active exact rule; the
                # unregistered-script pass below still rejects excluded code.
                if not active and rule['tag'] == 'script':
                    continue
                found = [n for n in by_tag.get(rule['tag'], []) if matches(n, rule)]
                expected = rule['count'] if active else 0
                if len(found) != expected:
                    errors.append(f"{path}: {item['id']} {rule['tag']} expected={expected} actual={len(found)}")
                if active:
                    approved.extend(found)
        for node in doc.nodes:
            if node['tag'] != 'script':
                continue
            # JSON-LD and inert JSON data are not executable scripts. Import maps are checked.
            if node['attrs'].get('type', '').lower().strip() in ('application/ld+json', 'application/json'):
                continue
            if not any(node is known for known in approved):
                errors.append(f"{path}: unregistered script {node['attrs'].get('src', '[inline]')}")
    for item in integrations:
        if item['enabled'] and not hits[item['id']]:
            errors.append(item['id'] + ': enabled integration matches no HTML pages')
    return errors, len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='actual deployment output, not repository root unless identical')
    parser.add_argument('--config', required=True, type=Path)
    baseline_mode = parser.add_mutually_exclusive_group(required=True)
    baseline_mode.add_argument('--baseline', type=Path, help='pre-change reviewed config snapshot')
    baseline_mode.add_argument('--first-inventory', action='store_true', help='explicit first inventory; no prior config baseline exists')
    parser.add_argument('--change-note', help='recorded explicit authorization reference for intended config changes')
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding='utf-8-sig'))
        if args.baseline:
            baseline = json.loads(args.baseline.read_text(encoding='utf-8-sig'))
            validate(baseline)
            if baseline != config and not (args.change_note or '').strip():
                raise ValueError('config changed: require review and --change-note with authorization reference; do not reset baseline')
        errors, count = check(args.root, config)
        if errors:
            for error in errors:
                print('FAIL:', error)
            return 1
        print(f'STATIC_PASS: {count} HTML files; runtime/CSP/privacy/backend checks remain required')
        if not args.baseline:
            print('BASELINE_NOT_CHECKED: only valid for first inventory or separately documented comparison')
        if args.change_note:
            print('CONFIG_CHANGE_REFERENCE:', args.change_note)
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        print('FAIL:', error)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
