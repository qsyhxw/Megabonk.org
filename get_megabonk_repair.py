"""Backward-compatible entry point for the leaderboard sync.

The active implementation lives in ``scripts/sync_leaderboard.py``.
"""

from scripts.sync_leaderboard import main


if __name__ == "__main__":
    raise SystemExit(main())
