#!/usr/bin/env python3
"""推送前在临时 worktree 中，按原样复现 validate-integrations 工作流。

由 .githooks/pre-push 调用；也可手动运行：python scripts/prepush_ci.py [--commit SHA]

改动阶段的快速自查（--fast，不替代推送前的全量预跑）：
  python scripts/prepush_ci.py --fast                  只跑共享检查（图片、布局、导航、URL、集成）
  python scripts/prepush_ci.py --fast --game hordes    再加上名称或命令里含 hordes 的 Rebuild 步骤
  --fast 直接在当前工作区运行（含未提交改动，Rebuild 步骤会就地重建生成物），不建临时 worktree，
  不受 paths 过滤影响，通常一两分钟；报错页面若不属于本专区（其他专区未重建而陈旧），以全量为准；用于“改一点、查一次”，避免把问题留到 39 步全量里才发现。

- 只读取被推送的提交，不修改你的工作区（在系统临时目录里建 detached worktree，用完即删）。
- 按工作流顺序逐个执行 run 步骤（bash -e，与 CI 相同）。某步失败后仍继续执行，
  最后汇总全部失败项，避免“修一个、冒一个”。
- 推送的改动没有命中工作流的 paths 过滤时直接跳过，与 GitHub 的触发规则一致。
- 按改动范围选择步骤（2026-11-23 批准，见 scripts/prepush_scope.py）：改动只落在某些专区的专属路径内时，
  只运行这些专区的重建步骤；校验步骤、发现页与任何共享改动始终全量。`--full` 可强制全量。
- 只对推送到 main 的提交生效。
- 步骤日志保存在 .git/prepush-logs/，不会进入 Git。
- 跳过检查：git push --no-verify
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepush_scope  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = '.github/workflows/validate-integrations.yml'
ZERO = '0' * 40
# --fast 默认只跑这些共享检查（按步骤名子串匹配）；专区自己的 Rebuild 步骤用 --game 追加
FAST_SHARED = ('guard rejects', 'game-scoped discovery', 'page-specific game images',
               'shared game-section layout', 'clean URLs', 'integration expectations')
# Windows 上 bash.exe 可能指向 WSL，这里优先使用 Git for Windows 自带的 bash
BASH = r'C:\Program Files\Git\bin\bash.exe' if os.name == 'nt' and Path(r'C:\Program Files\Git\bin\bash.exe').exists() else 'bash'


def git(*args, check=True):
    return subprocess.run(['git', *args], cwd=ROOT, check=check, capture_output=True,
                          encoding='utf-8', errors='replace').stdout.strip()


def glob_to_re(pattern):
    """把 GitHub paths 的 glob 转成正则：** 跨目录，* 不跨 /。"""
    out, i = '', 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out, i = out + '(?:.*/)?', i + 3
        elif pattern.startswith('**', i):
            out, i = out + '.*', i + 2
        elif pattern[i] == '*':
            out, i = out + '[^/]*', i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile('^' + out + '$')


def workflow_spec(commit):
    data = yaml.safe_load(git('show', f'{commit}:{WORKFLOW}'))
    on = data.get('on', data.get(True))  # PyYAML 把 on 解析为 True
    paths = ((on or {}).get('push') or {}).get('paths') or []
    steps = []
    for job in data['jobs'].values():
        # ci_summary.py 只在 CI 中汇总 toJSON(steps)，本地由本脚本自行汇总，跳过
        steps += [s for s in job['steps'] if 'run' in s and 'ci_summary.py' not in s['run']]
    return paths, steps


def execute(steps, cwd, tmp, base, logs, label):
    """按顺序执行步骤（bash -e，与 CI 相同），失败后继续，返回失败列表。"""
    # 从 pre-push 钩子触发时（尤其在 worktree 里推送）环境带有 GIT_DIR / GIT_INDEX_FILE 等变量；
    # 若传给步骤，测试里 cwd 在临时目录的 git init / add 会误操作真实仓库，必须清掉。
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(RUNNER_TEMP=str(tmp), PYTHONIOENCODING='utf-8')
    failures = []
    print(f'复现 {label}（{len(steps)} 个步骤），日志：{logs}')
    for i, step in enumerate(steps, 1):
        name = step.get('name') or f'步骤 {i}'
        step_env = dict(env)
        for k, v in (step.get('env') or {}).items():
            # 工作流里的 ${{ ... }} 只用于 BASE_SHA，这里替换为推送前的提交
            step_env[k] = base if '${{' in str(v) else str(v)
        print(f'[{i}/{len(steps)}] {name} ...', flush=True)
        r = subprocess.run([BASH, '-e', '-c', step['run']], cwd=cwd, env=step_env,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        log = logs / f'{i:02d}.log'
        log.write_text(r.stdout + r.stderr, encoding='utf-8')
        if r.returncode:
            failures.append((name, log, r.stdout + r.stderr))
            print('  失败（退出码 %d）' % r.returncode)
        else:
            print('  通过')
    return failures


def norm(text):
    return re.sub(r'[^a-z0-9]+', '', text.lower())


def fast(game):
    """工作区快速自查：共享检查 + 名称/命令含 game 的 Rebuild 步骤；不建 worktree，含未提交改动。"""
    _, steps = workflow_spec('HEAD')
    key = norm(game) if game else ''
    picked = []
    for s_ in steps:
        name = s_.get('name') or ''
        shared = any(f.lower() in name.lower() for f in FAST_SHARED)
        mine = bool(key) and (key in norm(name) or key in norm(s_['run']))
        if shared or mine:
            picked.append(s_)
    if game and not any(key in norm((x.get('name') or '') + x['run']) for x in picked):
        print(f'没有步骤匹配 --game {game}；只跑共享检查。')
    gdir = Path(git('rev-parse', '--git-common-dir').strip())
    gdir = gdir if gdir.is_absolute() else ROOT / gdir
    logs = gdir / 'prepush-logs' / 'fast'
    shutil.rmtree(logs, ignore_errors=True)
    logs.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp(prefix='prepush-fast-'))
    base = git('rev-parse', 'origin/main', check=False) or git('rev-parse', 'HEAD')
    try:
        failures = execute(picked, ROOT, tmp, base, logs, '工作区快速自查' + (f'（{game}）' if game else ''))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not failures:
        print(f'快速自查 {len(picked)} 个步骤全部通过。推送前仍须运行全量：python scripts/prepush_ci.py --commit HEAD')
        return 0
    print(f'\n快速自查 {len(failures)} 个步骤失败：')
    for name, log, _ in failures:
        print(f'  - {name}（{log}）')
    print('\n首个失败的末尾输出：')
    print('\n'.join(failures[0][2].splitlines()[-25:]))
    print('\n提示：--fast 只重建 --game 指定的专区，而 CI 会先重建全部专区再做共享检查；'
          '若报错的页面不属于本专区（已提交页面比其生成器旧），以全量预跑为准。')
    return 1


def run_for(commit, base, full=False):
    paths, steps = workflow_spec(commit)
    changed = git('diff', '--name-only', base, commit, check=False).splitlines() if base else ['*']
    if paths:
        patterns = [glob_to_re(p) for p in paths]
        if not any(p.match(f) for f in changed for p in patterns):
            print('推送的改动未命中 validate-integrations 的触发路径，跳过本地复现。')
            return 0
    if not full:
        steps, note = prepush_scope.select_steps(changed, steps)
        print(note)
    else:
        print('已指定 --full，全量运行。')

    # worktree 里 .git 是文件：日志放到共用 git 目录（git rev-parse --git-common-dir）
    gdir = Path(git('rev-parse', '--git-common-dir').strip())
    gdir = gdir if gdir.is_absolute() else ROOT / gdir
    logs = gdir / 'prepush-logs' / commit[:8]
    shutil.rmtree(logs, ignore_errors=True)
    logs.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp(prefix='prepush-ci-'))
    wt = tmp / 'tree'
    subprocess.run(['git', 'worktree', 'add', '--detach', str(wt), commit],
                   cwd=ROOT, check=True, capture_output=True)
    try:
        failures = execute(steps, wt, tmp, base, logs, commit[:8])
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=ROOT, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)

    if not failures:
        print(f'全部 {len(steps)} 个步骤通过，允许推送。')
        return 0
    print(f'\n共 {len(failures)} 个步骤失败：')
    for name, log, _ in failures:
        print(f'  - {name}（{log}）')
    print('\n首个失败的末尾输出：')
    print('\n'.join(failures[0][2].splitlines()[-25:]))
    print('\n已阻止推送。修复后再推送；紧急情况可用 git push --no-verify 跳过。')
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from-hook', action='store_true', help='从 pre-push 钩子调用，读取 stdin 的推送引用')
    ap.add_argument('--commit', default='HEAD', help='手动模式下要复现的提交')
    ap.add_argument('--fast', action='store_true', help='在当前工作区只跑共享检查（含未提交改动），见文件头说明')
    ap.add_argument('--game', default='', help='与 --fast 合用：追加名称或命令含该关键词的 Rebuild 步骤')
    ap.add_argument('--full', action='store_true', help='不按改动范围选择步骤，强制运行全部 39 步')
    a = ap.parse_args()
    if a.fast:
        return fast(a.game)

    pushes = []
    if a.from_hook:
        for line in sys.stdin:
            parts = line.split()
            if len(parts) != 4:
                continue
            local_ref, local_sha, remote_ref, remote_sha = parts
            if local_sha == ZERO or remote_ref != 'refs/heads/main':
                continue  # 删除分支，或推送到非 main：工作流不会在此运行
            base = remote_sha if remote_sha != ZERO else git('rev-parse', local_sha + '^', check=False)
            pushes.append((local_sha, base))
    else:
        commit = git('rev-parse', a.commit)
        pushes.append((commit, git('rev-parse', commit + '^', check=False)))

    rc = 0
    for commit, base in pushes:
        rc |= run_for(commit, base, full=a.full)
    return rc


if __name__ == '__main__':
    sys.exit(main())
