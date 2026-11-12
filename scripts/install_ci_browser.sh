#!/usr/bin/env bash
set -euo pipefail

# Avoid the Azure mirror DNS failures seen on hosted Ubuntu runners.
# These files are the mirror lists referenced by the runner's APT sources.
if [[ -f /etc/apt/apt-mirrors.txt ]]; then
  printf '%s\n' 'https://archive.ubuntu.com/ubuntu/' | sudo tee /etc/apt/apt-mirrors.txt >/dev/null
fi
if [[ -f /etc/apt/apt-mirrors-security.txt ]]; then
  printf '%s\n' 'https://security.ubuntu.com/ubuntu/' | sudo tee /etc/apt/apt-mirrors-security.txt >/dev/null
fi

python -m pip install --disable-pip-version-check playwright==1.54.0
for attempt in 1 2; do
  if timeout --signal=TERM --kill-after=10s 3m python -m playwright install --with-deps chromium; then
    exit 0
  fi
  if [[ "$attempt" == 1 ]]; then
    echo 'Browser installation failed or timed out; retrying once.' >&2
    sleep 5
  fi
done
echo 'Browser installation failed after two attempts.' >&2
exit 1
