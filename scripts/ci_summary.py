#!/usr/bin/env python3
"""汇总 validate-integrations 工作流中失败的步骤（只在 CI 最后一步运行）。

用法：STEPS_JSON='${{ toJSON(steps) }}' python scripts/ci_summary.py .github/workflows/validate-integrations.yml

每个 run 步骤都带有 always() 与 id，因此失败后仍会继续执行，本脚本把全部失败项列出，
并写入 GitHub Step Summary。只要存在失败就以非零退出，保证工作流仍然标记为失败。
"""
import json
import os
import re
import sys
from pathlib import Path


def step_names(workflow):
    """从工作流文件读取 id -> 步骤名，id 紧跟在 name 行之后。"""
    names = {}
    lines = Path(workflow).read_text(encoding='utf-8').splitlines()
    for line, nxt in zip(lines, lines[1:]):
        m = re.match(r'\s*- name: (.+)$', line)
        i = re.match(r'\s*id: (\S+)$', nxt)
        if m and i:
            names[i.group(1)] = m.group(1).strip()
    return names


def main():
    workflow = sys.argv[1]
    steps = json.loads(os.environ['STEPS_JSON'])
    names = step_names(workflow)
    failed = [(sid, names.get(sid, sid)) for sid, s in steps.items() if s.get('outcome') == 'failure']
    total = sum(1 for s in steps.values() if s.get('outcome') in ('success', 'failure'))

    lines = [f'### 集成检查汇总', f'共执行 {total} 个步骤，失败 {len(failed)} 个。']
    if failed:
        lines.append('')
        lines.append('失败步骤（按工作流顺序，首个失败通常是根因，其后的可能是连带失败）：')
        lines += [f'- {name}' for _, name in failed]
    else:
        lines.append('全部步骤通过。')
    report = '\n'.join(lines)
    print(report)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as f:
            f.write(report + '\n')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
