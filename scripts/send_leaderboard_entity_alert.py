#!/usr/bin/env python3
"""Email leaderboard entity coverage failures through the existing Gmail secrets."""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def load_report(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    username = os.environ.get("GMAIL_USERNAME")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("PATCH_ALERT_EMAIL")
    if not all((username, password, recipient)):
        print(
            "::error::Leaderboard entity alert failed because Gmail Secrets "
            "are incomplete."
        )
        return 1

    report = load_report(args.report)
    gaps = report.get("gaps", [])
    action_url = (
        f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
        f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/"
        f"{os.environ.get('GITHUB_RUN_ID', '')}"
    )
    if gaps:
        title = f"排行榜发现 {len(gaps)} 个实体资料缺口"
        details = [
            f"- [{gap.get('sourceType', 'unknown')}] {gap.get('id', 'unknown')}: "
            f"{gap.get('reason', 'unknown reason')}"
            for gap in gaps
        ]
    else:
        title = "排行榜自动同步任务失败"
        details = [
            "- 未生成实体缺口报告，可能是抓取、解析、测试或 Git 推送步骤失败。"
        ]

    body = "\n".join(
        [
            title,
            "",
            *details,
            "",
            "自动发布已停止，请核实实体类型，并补充详情页和图片/图标后重新运行任务。",
            f"GitHub Actions: {action_url}",
        ]
    )
    message = EmailMessage()
    message["Subject"] = f"Megabonk 警报：{title}"
    message["From"] = username
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30
    ) as smtp:
        smtp.login(username, password.replace(" ", ""))
        smtp.send_message(message)
    print(f"Leaderboard entity alert sent to {recipient}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
