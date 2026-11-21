#!/usr/bin/env python3
"""推送前在临时 worktree 中，按原样复现 validate-integrations 工作流。

由 .githooks/pre-push 调用；也可手动运行：python scripts/prepush_ci.py [--commit SHA]

- 只读取被推送的提交，不修改你的工作区（在系统临时目录里建 detached worktree，用完即删）。
- 按工作流顺序逐个执行 run 步骤（bash -e，与 CI 相同）。某步失败后仍继续执行，
  最后汇总全部失败项，避免“修一个、冒一个”。
- 推送的改动没有命中工作流的 paths 过滤时直接跳过，与 GitHub 的触发规则一致。
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

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = '.github/workflows/validate-integrations.yml'
ZERO = '0' * 40
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


def run_for(commit, base):
    paths, steps = workflow_spec(commit)
    if paths:
        changed = git('diff', '--name-only', base, commit, check=False).splitlines() if base else ['*']
        patterns = [glob_to_re(p) for p in paths]
        if not any(p.match(f) for f in changed for p in patterns):
            print('推送的改动未命中 validate-integrations 的触发路径，跳过本地复现。')
            return 0

    # worktree 里 .git 是文件：日志放到共用 git 目录（git rev-parse --git-common-dir）
    gdir = Path(git('rev-parse', '--git-common-dir'))
    gdir = gdir if gdir.is_absolute() else ROOT / gdir
    logs = gdir / 'prepush-logs' / commit[:8]
    shutil.rmtree(logs, ignore_errors=True)
    logs.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp(prefix='prepush-ci-'))
    wt = tmp / 'tree'
    subprocess.run(['git', 'worktree', 'add', '--detach', str(wt), commit],
                   cwd=ROOT, check=True, capture_output=True)
    env = dict(os.environ, RUNNER_TEMP=str(tmp), PYTHONIOENCODING='utf-8')
    failures = []
    print(f'在临时目录复现 {commit[:8]}（{len(steps)} 个步骤），日志：{logs}')
    try:
        for i, step in enumerate(steps, 1):
            name = step.get('name') or f'步骤 {i}'
            step_env = dict(env)
            for k, v in (step.get('env') or {}).items():
                # 工作流里的 ${{ ... }} 只用于 BASE_SHA，这里替换为推送前的提交
                step_env[k] = base if '${{' in str(v) else str(v)
            print(f'[{i}/{len(steps)}] {name} ...', flush=True)
            r = subprocess.run([BASH, '-e', '-c', step['run']], cwd=wt, env=step_env,
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            log = logs / f'{i:02d}.log'
            log.write_text(r.stdout + r.stderr, encoding='utf-8')
            if r.returncode:
                failures.append((name, log, r.stdout + r.stderr))
                print('  失败（退出码 %d）' % r.returncode)
            else:
                print('  通过')
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
    a = ap.parse_args()

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
        rc |= run_for(commit, base)
    return rc


if __name__ == '__main__':
    sys.exit(main())
