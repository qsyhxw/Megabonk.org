#!/usr/bin/env python3
"""Azeroth 同步通知（SOP 05 §2.9.1 v3.27）。仅标准库，只发邮件/开 Issue，不改任何站点文件。

  python scripts/azeroth_notify.py changed  [--report diff.json] [--dry-run]
  python scripts/azeroth_notify.py failure  [--dry-run]
  python scripts/azeroth_notify.py backlog  [--days 14] [--dry-run]
  python scripts/azeroth_notify.py test     # 发一封测试邮件

环境变量：GMAIL_USERNAME / GMAIL_APP_PASSWORD / PATCH_ALERT_EMAIL（缺失只告警，不报错）、
GITHUB_TOKEN / GITHUB_REPOSITORY（开 Issue 用，缺失则只发邮件）。
"""
import argparse, datetime, json, os, smtplib, ssl, urllib.request
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "megabonk.org/azeroth-survivors"
LABEL = "auto-sentinel"


def run_url():
    rid = os.environ.get("GITHUB_RUN_ID")
    if not rid:
        return ""
    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{rid}"


def send_mail(subject, body, dry):
    if dry:
        print(f"--- DRY-RUN email: {subject}\n{body}")
        return
    need = ("GMAIL_USERNAME", "GMAIL_APP_PASSWORD", "PATCH_ALERT_EMAIL")
    if not all(os.environ.get(k, "").strip() for k in need):
        print("::warning::Gmail 密钥缺失，未发送邮件")
        return
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, os.environ["GMAIL_USERNAME"].strip(), os.environ["PATCH_ALERT_EMAIL"].strip()
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30) as s:
        s.login(os.environ["GMAIL_USERNAME"].strip(), os.environ["GMAIL_APP_PASSWORD"].replace(" ", ""))
        s.send_message(msg)
    print("邮件已发送到", msg["To"])


def open_issue(title, body, dry):
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if dry or not (repo and token):
        print(f"--- Issue（未创建）: {title}")
        return ""

    def call(method, path, payload):
        req = urllib.request.Request("https://api.github.com" + path, method=method, data=json.dumps(payload).encode(),
                                     headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "User-Agent": "azeroth-notify"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"null")
    try:
        call("POST", f"/repos/{repo}/labels", {"name": LABEL, "color": "1d76db"})
    except Exception:
        pass  # 标签已存在
    try:
        return call("POST", f"/repos/{repo}/issues", {"title": title, "body": body, "labels": [LABEL]})["html_url"]
    except Exception as e:
        print("::warning::创建 Issue 失败：", e)
        return ""


def load_state():
    return json.loads((ROOT / "data/azeroth-sync.json").read_text(encoding="utf8"))


def pending_lines(state, limit=40):
    rows = sorted(state.get("pending", {}).items(), key=lambda kv: kv[1].get("since", ""))
    out = [f"- {k}（自 {v.get('since')}，版本 {v.get('version')}）" for k, v in rows[:limit]]
    if len(rows) > limit:
        out.append(f"- …另有 {len(rows) - limit} 页")
    return out


def find_report(path):
    if not path:
        return {}
    p = Path(path)
    if p.is_dir():
        c = sorted(p.rglob("azeroth-diff.json"))
        p = c[0] if c else None
    try:
        return json.loads(p.read_text(encoding="utf8")) if p and p.exists() else {}
    except Exception:
        return {}


def cmd_changed(a):
    st, rep = load_state(), find_report(a.report)
    ver = st["observed"]["version"]
    sc = rep.get("source_changes", st.get("last_changes", {}))
    domains = ", ".join(rep.get("domains", [])) or "无"
    affected = rep.get("affected_pages", st.get("last_changes", {}).get("affected_pages", []))
    title = f"原版数据已同步（{ver}）：新增 {sc.get('added', 0)} / 删除 {sc.get('removed', 0)} / 变更 {sc.get('changed', 0)}"
    body = [f"{SITE} 的原版来源有变化，已自动同步参考数据并推送（仅白名单字段）。", "",
            f"- 版本：{ver}（构建 {st['observed'].get('build')}）", f"- 同步的数据域：{domains}",
            f"- 受影响页面：{len(affected)} 个", f"- 待人工复核页面总数：{len(st.get('pending', {}))}", "",
            "待复核清单（最早的在前）：", *pending_lines(st), "",
            "编辑性结论（构筑、Tier、推荐）不会自动改，需人工复核。",
            f"处理方式：把本 Issue 链接交给 `/weihu {SITE} 事件 材料:<Issue链接>`；处理完写结果并关闭。",
            f"运行记录：{run_url()}"]
    text = "\n".join(body)
    url = open_issue("[Azeroth] " + title, text, a.dry_run)
    send_mail(f"[{SITE}] {title}", text + (f"\nIssue：{url}" if url else "") + "\n此邮件由 GitHub Actions 自动发送。", a.dry_run)


def cmd_failure(a):
    text = (f"{SITE} 的 Azeroth 原版同步工作流本次运行失败（页面未被改动，或发布被校验拦截）。\n\n运行记录：{run_url()}\n\n"
            f"请查看日志；连续失败时用 `/weihu {SITE}` 处理。\n此邮件由 GitHub Actions 自动发送。")
    send_mail(f"[{SITE}] 同步失败：sync-azeroth", text, a.dry_run)


def cmd_backlog(a):
    st = load_state()
    today = datetime.date.today()
    old = {k: v for k, v in st.get("pending", {}).items()
           if (today - datetime.date.fromisoformat(v["since"])).days >= a.days}
    if not old:
        print("没有超过", a.days, "天的待复核页面")
        return
    lines = [f"- {k}（自 {v['since']}，已 {(today - datetime.date.fromisoformat(v['since'])).days} 天，版本 {v['version']}）"
             for k, v in sorted(old.items(), key=lambda kv: kv[1]["since"])]
    text = (f"{SITE} 有 {len(old)} 个页面的编辑性内容超过 {a.days} 天未复核（共 {len(st.get('pending', {}))} 页待复核）：\n\n" + "\n".join(lines) +
            f"\n\n处理方式：交给 `/weihu {SITE} 事件`，按页核对构筑/Tier/推荐是否仍适用当前版本 {st['observed']['version']}；复核后清除 pending。\n"
            "每周一汇总一次。\n此邮件由 GitHub Actions 自动发送。")
    send_mail(f"[{SITE}] {len(old)} 页待复核已超 {a.days} 天", text, a.dry_run)


def cmd_test(a):
    send_mail(f"[{SITE}] 测试邮件：Azeroth 同步通知", f"这是一封测试邮件，说明 sync-azeroth 的通知渠道可用。\n运行记录：{run_url()}\n", a.dry_run)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["changed", "failure", "backlog", "test"])
    ap.add_argument("--report")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    {"changed": cmd_changed, "failure": cmd_failure, "backlog": cmd_backlog, "test": cmd_test}[a.mode](a)
