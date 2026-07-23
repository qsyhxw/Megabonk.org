"""Send Patch Notes update and workflow failure alerts through Gmail SMTP."""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import Mapping


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
PATCH_PAGE_URL = "https://megabonk.org/guides/patch-notes/"
REQUIRED_SECRETS = ("GMAIL_USERNAME", "GMAIL_APP_PASSWORD", "PATCH_ALERT_EMAIL")


def github_urls(environment: Mapping[str, str]) -> tuple[str, str]:
    repository = environment.get("GITHUB_REPOSITORY", "qsyhxw/Megabonk.org")
    run_id = environment.get("GITHUB_RUN_ID", "")
    commit_sha = environment.get("PATCH_COMMIT_SHA", "")
    run_url = f"https://github.com/{repository}/actions/runs/{run_id}" if run_id else ""
    commit_url = f"https://github.com/{repository}/commit/{commit_sha}" if commit_sha else ""
    return run_url, commit_url


def build_update_email(
    state: Mapping[str, object], environment: Mapping[str, str]
) -> tuple[str, str]:
    version = str(state["latest_version"])
    versions = state.get("versions", {})
    record = versions.get(version, {}) if isinstance(versions, dict) else {}
    title = str(record.get("title", f"Megabonk V{version}"))
    release_date = str(record.get("release_date", "Unknown"))
    source_url = str(record.get("source_url", ""))
    bullets = record.get("bullets", [])
    bullet_lines = "\n".join(f"- {value}" for value in list(bullets)[:12])
    new_versions = environment.get("PATCH_NEW_VERSIONS", "").strip()
    latest_edited = environment.get("PATCH_LATEST_EDITED", "false") == "true"
    update_type = "新版本" if new_versions else "当前版本追加 Hotfix"
    if latest_edited and not new_versions:
        update_type = "官方公告追加或修改 Hotfix"
    run_url, commit_url = github_urls(environment)

    subject = f"[Megabonk] V{version} 更新提醒｜请检查相关页面"
    body = f"""检测到 Megabonk 官方版本内容发生变化，Patch Notes 页面已自动更新并推送。

更新类型：{update_type}
版本：V{version}
公告标题：{title}
发布日期：{release_date}
官方来源：{source_url or '未提供'}
网站页面：{PATCH_PAGE_URL}
GitHub 提交：{commit_url or '未提供'}
Actions 运行：{run_url or '未提供'}

本次更新要点：
{bullet_lines or '- 官方公告没有可提取的条目，请直接查看来源。'}

建议检查范围：
- 角色、被动与基础属性
- 武器、物品、Tome 和解锁条件
- Best Build 与 Tier List
- Boss、敌人、地图和机制页面
- 旧数值、旧描述及相关内链

此邮件由 Megabonk.org GitHub Actions 自动发送。
"""
    return subject, body


def build_test_email(environment: Mapping[str, str]) -> tuple[str, str]:
    run_url, _ = github_urls(environment)
    subject = "[Megabonk] Patch Notes 邮件通知测试成功"
    body = f"""Gmail SMTP 邮件通知配置成功。

以后检测到新版本或官方追加 Hotfix 时，此邮箱会收到自动提醒。
本次测试运行：{run_url or '未提供'}

此邮件由 Megabonk.org GitHub Actions 手动测试发送。
"""
    return subject, body


def build_failure_email(environment: Mapping[str, str]) -> tuple[str, str]:
    run_url, _ = github_urls(environment)
    workflow = environment.get("GITHUB_WORKFLOW", "Update Megabonk Patch Notes")
    subject = "[Megabonk] Patch Notes 自动更新失败"
    body = f"""Megabonk Patch Notes 自动更新工作流执行失败。

工作流：{workflow}
Actions 运行：{run_url or '请前往 GitHub Actions 查看'}

请检查 Steam 抓取、页面校验、Git 推送或邮件配置是否出现问题。
此邮件由 Megabonk.org GitHub Actions 自动发送。
"""
    return subject, body


def send_email(subject: str, body: str, environment: Mapping[str, str]) -> bool:
    missing = [name for name in REQUIRED_SECRETS if not environment.get(name, "").strip()]
    if missing:
        print(
            "::warning::Patch alert email skipped; missing GitHub Secrets: "
            + ", ".join(missing)
        )
        return False

    username = environment["GMAIL_USERNAME"].strip()
    password = environment["GMAIL_APP_PASSWORD"].replace(" ", "")
    recipient = environment["PATCH_ALERT_EMAIL"].strip()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = username
    message["To"] = recipient
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
    print(f"Patch alert email sent to {recipient}.")
    return True


def main() -> int:
    kind = sys.argv[1] if len(sys.argv) > 1 else "update"
    if kind == "update":
        state = json.loads(
            Path("data/patch-notes-state.json").read_text(encoding="utf-8")
        )
        subject, body = build_update_email(state, os.environ)
    elif kind == "test":
        subject, body = build_test_email(os.environ)
    elif kind == "failure":
        subject, body = build_failure_email(os.environ)
    else:
        print(f"Unknown alert type: {kind}", file=sys.stderr)
        return 2

    send_email(subject, body, os.environ)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
