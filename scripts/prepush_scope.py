"""按改动范围选择推送前预跑的重建步骤（方案见 _private/prepush-scope/PLAN.md，2026-11-23 批准）。

规则（默认安全：拿不准一律全量）：
- 改动集合为空、或有任何文件不在某个专区的专属路径内 → 运行全部步骤。
- 改动只落在一个或多个专区的专属路径内 → 只保留这些专区的重建步骤；
  其他专区的重建步骤跳过；校验步骤、无法归属的重建步骤、会写共享目录的重建步骤始终保留。

专属路径来自 2026-11-23 的写入探测（修改时间变化法，见 PLAN）。未登记的生成脚本不会被跳过。
本模块是纯函数，不调用 git，便于 tests/test_prepush_scope.py 单独测试。
"""
import json
import re

# 游戏 → 专属路径前缀（以 '/' 结尾为目录，其余为文件名前缀）与其重建脚本。
# 只登记探测确认“写入只落在专属路径”的专区；写共享目录的步骤（主站长尾、PokeDive、Vampire Survivors）
# 不在此表中，因此始终运行。
GAMES = {
    'pokebonk': {'dirs': ['pokebonk/'], 'files': ['data/pokebonk-'],
                 'scripts': ['derive_pokebonk_evolution.py', 'pokebonk_loadouts.py', 'build_pokebonk.py']},
    'poke-survivor': {'dirs': ['poke-survivor/'], 'files': [], 'scripts': ['build_poke_survivor.py']},
    'survivor-ace': {'dirs': ['survivor-ace/'], 'files': [], 'scripts': ['build_survivor_ace.py']},
    'azeroth-survivors': {'dirs': ['azeroth-survivors/'], 'files': ['data/azeroth-planner.json'],
                          'scripts': ['build_azeroth_survivors.py']},
    'arena-of-champions': {'dirs': ['arena-of-champions/'], 'files': [], 'scripts': ['build_arena_champions.py']},
    'ball-x-pit': {'dirs': ['ball-x-pit/'], 'files': [], 'scripts': ['build_ball_x_pit.py']},
    'soulstone-survivors': {'dirs': ['soulstone-survivors/'], 'files': [], 'scripts': ['build_soulstone_survivors.py']},
    'warhammer-survivors': {'dirs': ['warhammer-survivors/'], 'files': [], 'scripts': ['build_warhammer_survivors.py']},
    'd2-survivors': {'dirs': ['d2-survivors/'], 'files': [], 'scripts': ['build_d2_survivors.py']},
    'spires-of-azeroth': {'dirs': ['spires-of-azeroth/'], 'files': [], 'scripts': ['build_spires_of_azeroth.py']},
    'pokearena-2d': {'dirs': ['pokearena-2d/'], 'files': [], 'scripts': ['build_pokearena.py']},
    'pokepath': {'dirs': ['pokepath/'], 'files': [], 'scripts': ['build_pokepath.py']},
    'revenant-survivors': {'dirs': ['revenant-survivors/'], 'files': [], 'scripts': ['build_revenant_survivors.py']},
    'midgard-survivors': {'dirs': ['midgard-survivors/'], 'files': [], 'scripts': ['build_midgard_survivors.py']},
    'brotato': {'dirs': ['brotato/'], 'files': [], 'scripts': ['build_brotato.py']},
    'pokelit': {'dirs': ['pokelit/'], 'files': [], 'scripts': ['build_pokelit.py']},
    'pokemon-battlegrounds': {'dirs': ['pokemon-battlegrounds/'], 'files': [], 'scripts': ['build_pokemon_battlegrounds.py']},
    'poke-isaac': {'dirs': ['poke-isaac/'], 'files': [], 'scripts': ['build_pokeisaac.py']},
    'pokeversus': {'dirs': ['pokeversus/'], 'files': [], 'scripts': ['build_pokeversus.py']},
    'poke-solaire': {'dirs': ['poke-solaire/'], 'files': [], 'scripts': ['build_poke_solaire.py']},
    'pokerogue': {'dirs': ['pokerogue/'], 'files': [], 'scripts': ['build_pokerogue.py']},
    'hordes-of-azeroth': {'dirs': ['hordes-of-azeroth/'], 'files': [], 'scripts': ['build_hordes_of_azeroth.py']},
    'risk-of-rain-2': {'dirs': ['risk-of-rain-2/', 'assets/risk-of-rain-2/'], 'files': ['data/risk-of-rain-2'],
                       'scripts': ['build_risk_of_rain_2.py']},
    'mythic-survivors': {'dirs': ['mythic-survivors/'], 'files': [], 'scripts': ['build_mythic_survivors.py']},
}

_SCRIPT_RE = re.compile(r'scripts/([A-Za-z0-9_]+\.py)')


def owner_of(path):
    """返回改动路径所属的游戏；不属于任何游戏的专属路径返回 None。"""
    for game, spec in GAMES.items():
        if any(path.startswith(d) for d in spec['dirs']) or any(path.startswith(f) for f in spec['files']):
            return game
    return None


def step_game(step):
    """重建步骤所属游戏：步骤命令中的生成脚本属于哪个专区。无法归属返回 None（始终保留）。"""
    run = step.get('run') or ''
    scripts = set(_SCRIPT_RE.findall(run))
    for game, spec in GAMES.items():
        if scripts & set(spec['scripts']):
            return game
    return None


def is_rebuild(step):
    name = step.get('name') or ''
    return name.startswith('Rebuild')


def touched_games(changed):
    """改动全部落在专区专属路径内时返回涉及的专区集合；否则（含未知）返回 None。"""
    if not changed or '*' in changed:
        return None
    touched = set()
    for path in changed:
        game = owner_of(path)
        if game is None:
            return None
        touched.add(game)
    return touched


def select_steps(changed, steps):
    """返回 (保留的步骤列表, 说明文字)。changed 为改动路径列表，changed 为空或含 '*' 时全量。"""
    if not changed or '*' in changed:
        return list(steps), '改动集合未知，全量运行'
    touched = set()
    for path in changed:
        game = owner_of(path)
        if game is None:
            return list(steps), f'改动 {path} 不在任何专区的专属路径内，全量运行'
        touched.add(game)
    kept, skipped = [], []
    for step in steps:
        game = step_game(step)
        if is_rebuild(step) and game is not None and game not in touched:
            skipped.append(step.get('name') or '?')
            continue
        kept.append(step)
    note = f'改动仅属于专区 {", ".join(sorted(touched))}；跳过 {len(skipped)} 个其他专区的重建步骤'
    return kept, note


# ---- 登记文件按条目归属（v3.30）----
# 新页上线必然改这几个全站登记文件；若只看文件名会一律判“共享→全量”，让单专区推送白跑全量。
# 这里逐条比较新旧内容：只要变化的条目全部落在专区专属路径内，就把该文件替换成这些条目路径参与归属判断；
# 任何一处无法证明（解析失败、非条目区域有改动、条目不属于专区）都保留原文件名，仍按共享处理。
REGISTRY_FILES = ('pages_list.txt', 'sitemap.xml', 'data/content-dates.json', 'data/game-seo.json')
_HOST_RE = re.compile(r'^https?://[^/]+/?')
_URL_BLOCK_RE = re.compile(r'<url>.*?</url>', re.S)
_LOC_RE = re.compile(r'<loc>\s*([^<]+?)\s*</loc>')


def _rel(entry):
    return _HOST_RE.sub('', entry.strip())


def _changed_keys(old, new):
    return {k for k in set(old) | set(new) if old.get(k) != new.get(k)}


def registry_entries(path, old, new):
    """返回该登记文件中变化的条目（相对站点根的路径）；无法证明时返回 None。"""
    if old is None or new is None:
        return None
    try:
        if path == 'pages_list.txt':
            a = {l.strip() for l in old.splitlines() if l.strip()}
            b = {l.strip() for l in new.splitlines() if l.strip()}
            return {_rel(x) for x in a ^ b}
        if path == 'sitemap.xml':
            if re.sub(r'\s+', '', _URL_BLOCK_RE.sub('', old)) != re.sub(r'\s+', '', _URL_BLOCK_RE.sub('', new)):
                return None

            def blocks(text):
                out = {}
                for blk in _URL_BLOCK_RE.findall(text):
                    m = _LOC_RE.search(blk)
                    if not m:
                        raise ValueError('url block without loc')
                    out[m.group(1)] = re.sub(r'\s+', ' ', blk)
                return out
            return {_rel(k) for k in _changed_keys(blocks(old), blocks(new))}
        if path == 'data/content-dates.json':
            return {_rel(k) for k in _changed_keys(json.loads(old), json.loads(new))}
        if path == 'data/game-seo.json':
            o, n = json.loads(old), json.loads(new)
            if {k: v for k, v in o.items() if k != 'pages'} != {k: v for k, v in n.items() if k != 'pages'}:
                return None
            return {_rel(k) for k in _changed_keys(o.get('pages', {}), n.get('pages', {}))}
    except (ValueError, AttributeError, TypeError):
        return None
    return None


def expand_registry(changed, read_old, read_new):
    """把改动列表里的登记文件换成其变化条目；read_old/read_new(path) 返回文本，不存在返回 None。"""
    if not changed or '*' in changed:
        return list(changed)
    out = []
    for path in changed:
        if path in REGISTRY_FILES:
            entries = registry_entries(path, read_old(path), read_new(path))
            if entries is not None:
                out.extend(sorted(entries))
                continue
        out.append(path)
    return out
