"""Use the actual pre-push/PR Git configuration as the CI baseline."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
before = os.environ.get('BASE_SHA', '')
prior = subprocess.run(['git', 'show', before + ':config/integrations.json'], cwd=ROOT, capture_output=True) if before and set(before) != {'0'} else None
with tempfile.TemporaryDirectory() as temp:
    baseline = Path(temp)/'integrations.json'
    args = [sys.executable, str(ROOT/'scripts/verify_integrations.py'), '--baseline', str(baseline)]
    if prior and prior.returncode == 0:
        baseline.write_bytes(prior.stdout)
        current = json.loads((ROOT/'config/integrations.json').read_text(encoding='utf-8'))
        previous = json.loads(prior.stdout)
        if current != previous:
            # A change reference is an auditable review record, not an automatic
            # authorization. Reviewers still inspect the precise config diff.
            note = current.get('change_reference', '')
            if not note:
                raise SystemExit('FAIL: changed config has no explicit change reference')
            args += ['--change-note', note]
    else:
        baseline.write_bytes((ROOT/'config/integrations.initial.json').read_bytes())
        args += ['--change-note', 'ROADMAP ITERATION-EXEC 2026-10-25 first inventory; no prior machine config existed']
    raise SystemExit(subprocess.run(args, cwd=ROOT).returncode)
