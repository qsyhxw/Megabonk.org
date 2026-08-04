#!/usr/bin/env python3
"""Send consistent automation alerts through Gmail."""

from __future__ import annotations

import argparse
import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Mapping


REQUIRED_SECRETS = ("GMAIL_USERNAME", "GMAIL_APP_PASSWORD", "PATCH_ALERT_EMAIL")


def run_url(environment: Mapping[str, str]) -> str:
    server = environment.get("GITHUB_SERVER_URL", "https://github.com")
    repository = environment.get("GITHUB_REPOSITORY", "qsyhxw/Megabonk.org")
    run_id = environment.get("GITHUB_RUN_ID", "")
    return f"{server}/{repository}/actions/runs/{run_id}" if run_id else f"{server}/{repository}/actions"


def build_message(kind: str, name: str, environment: Mapping[str, str]) -> tuple[str, str]:
    if kind == "failure":
        subject = f"[Megabonk] 自动任务失败：{name}"
        intro = f"Megabonk.org 自动任务“{name}”执行失败或超时。"
    elif kind == "heartbeat":
        subject = f"[Megabonk] 每日自动化健康报告：{name}"
        intro = f"Megabonk.org 自动任务“{name}”的线上健康检查已通过。"
    else:
        subject = f"[Megabonk] 邮件通知测试成功：{name}"
        intro = f"Megabonk.org 自动任务“{name}”的 Gmail 通知配置正常。"
    lines = [intro, "", f"工作流：{name}", f"GitHub Actions：{run_url(environment)}"]
    details = environment.get("AUTOMATION_DETAILS", "").strip()
    if details:
        lines.append(f"说明：{details}")
    lines.extend(["", "此邮件由 Megabonk.org GitHub Actions 自动发送。"])
    return subject, "\n".join(lines) + "\n"


def send_email(subject: str, body: str, environment: Mapping[str, str]) -> None:
    missing = [key for key in REQUIRED_SECRETS if not environment.get(key, "").strip()]
    if missing:
        raise RuntimeError("Missing required GitHub Secrets: " + ", ".join(missing))
    username = environment["GMAIL_USERNAME"].strip()
    password = environment["GMAIL_APP_PASSWORD"].replace(" ", "")
    recipient = environment["PATCH_ALERT_EMAIL"].strip()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = username
    message["To"] = recipient
    message.set_content(body)
    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30
    ) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
    print(f"Automation alert sent to {recipient}.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("failure", "test", "heartbeat"))
    parser.add_argument("--name", default=os.environ.get("GITHUB_WORKFLOW", "Megabonk Automation"))
    args = parser.parse_args()
    try:
        subject, body = build_message(args.kind, args.name, os.environ)
        send_email(subject, body, os.environ)
    except Exception as error:
        print(f"::error::Automation email could not be sent: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
