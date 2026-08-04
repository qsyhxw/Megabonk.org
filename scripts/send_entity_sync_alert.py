#!/usr/bin/env python3
"""Send entity-monitor updates through the existing Gmail SMTP secrets."""

from __future__ import annotations

import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


REPORT = Path("data/wiki-entity-sync-report.json")


def main() -> int:
    username = os.environ.get("GMAIL_USERNAME")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("PATCH_ALERT_EMAIL")
    if not all((username, password, recipient)):
        print("::error::Entity alert failed because Gmail Secrets are incomplete.")
        return 1

    report = (
        json.loads(REPORT.read_text(encoding="utf-8"))
        if REPORT.exists()
        else {}
    )
    new_entities = report.get("newSincePrevious", [])
    removed = report.get("removedSincePrevious", [])
    downloads = report.get("downloadedLicensedImages", [])
    gaps = report.get("catalogGaps", [])

    lines = [
        "Megabonk 实体目录监控发现变化。",
        "",
        f"新增实体：{len(new_entities)}",
        *[f"- [{item['type']}] {item['name']}" for item in new_entities],
        "",
        f"外站已移除：{len(removed)}",
        *[f"- [{item['type']}] {item['name']}" for item in removed],
        "",
        f"已下载许可明确的图片：{len(downloads)}",
        *[f"- {item['entity']} -> {item['localPath']}" for item in downloads],
        "",
        f"当前仍需人工审核的本站目录缺口：{len(gaps)}",
        "",
        "自动化只生成审核草稿，不会未经双来源核验直接发布正式页面。",
        f"GitHub Actions: {os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
        f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions",
    ]

    message = EmailMessage()
    message["Subject"] = (
        f"Megabonk 实体目录变化：新增 {len(new_entities)}，图片 {len(downloads)}"
    )
    message["From"] = username
    message["To"] = recipient
    message.set_content("\n".join(lines))

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30
    ) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
    print(f"Entity sync alert sent to {recipient}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
