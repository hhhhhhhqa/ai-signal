#!/usr/bin/env python3
"""Central-side health check: surface the failures that exit code 0 hides.

An unattended daily job fails quietly. An expired X cookie, a logged-out
WeChat session, an ASR key that ran out of credit, a dependency that vanished
when the venv moved — none of these make ``run.sh`` exit non-zero, they just
leave yesterday's feed sitting there looking fine. This script inspects what
the run actually produced and shouts through whatever channel is configured.

Run it at the end of ``run.sh``; it needs no arguments. Exit code is 1 when
something is broken, 0 otherwise, so a manual run reads like a normal command.

Alert channels, all optional and additive (set in .env):
  HEALTH_EMAIL_TO      recipient; enables email. Send via SMTP when
                       HEALTH_SMTP_USER/HEALTH_SMTP_PASS are set (host and port
                       default to Gmail), otherwise via Resend when
                       RESEND_API_KEY is set.
  HEALTH_WEBHOOK_URL   飞书 / 企业微信 自定义机器人 webhook — pushes to phone
  HEALTH_TG_BOT_TOKEN  Telegram bot token (needs HEALTH_TG_CHAT_ID too)
  HEALTH_TG_CHAT_ID    Telegram chat id
A macOS notification is always posted when something is wrong, so the check is
useful with zero configuration.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
FEEDS_DIR = ROOT / "feeds"
CONFIG_PATH = ROOT / "config" / "sources.json"
STATE_PATH = Path.home() / ".ai-signal" / "health.json"

# The daily job runs every 24h; allow a couple of hours of slack before a feed
# that failed to refresh counts as stale.
MAX_FEED_AGE_HOURS = 26
# wewe-rss pulls on its own schedule, which can sit close to a day behind
# without anything being wrong. A dead 微信读书 session stays dead, so a wider
# window still catches it in time for the next digest — without crying wolf.
MAX_WECHAT_SYNC_AGE_HOURS = 48

OK, WARN, FAIL = "ok", "warn", "fail"
ICON = {OK: "✅", WARN: "⚠️", FAIL: "❌"}

# Central-side imports that have silently gone missing before. feed generation
# catches the ImportError per person/episode, so the run still "succeeds".
REQUIRED_MODULES = {
    "httpx": "拉取所有 HTTP 来源",
    "twscrape": "抓 Twitter/X",
    "yt_dlp": "人物追踪的 YouTube 搜索",
    "youtube_transcript_api": "播客的 YouTube 字幕",
}

# Volc ASR has no balance endpoint for an API-key-only credential, so an empty
# account can only be recognised by what the transcription error says.
BILLING_HINTS = ("quota", "balance", "arrear", "insufficient", "not activated",
                 "余额", "欠费", "配额", "资源包", "未开通", "已过期")


def log(msg):
    print(msg, flush=True)


def feed_age_hours(feed):
    generated = feed.get("generated_at")
    if not generated:
        return None
    try:
        stamp = datetime.fromisoformat(generated)
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - stamp).total_seconds() / 3600


def load_feed(name):
    try:
        return json.loads((FEEDS_DIR / name).read_text(encoding="utf-8"))
    except Exception:
        return None


def result(status, title, detail, fix=""):
    return {"status": status, "title": title, "detail": detail, "fix": fix}


def check_dependencies():
    """A moved or rebuilt venv drops packages; feed generation degrades silently."""
    import importlib

    missing = []
    for module, purpose in REQUIRED_MODULES.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(f"{module}({purpose})")
    if missing:
        return result(
            FAIL, "依赖", f"缺少 {', '.join(missing)}",
            f"{ROOT}/.venv/bin/python -m pip install -r requirements-central.txt",
        )
    return result(OK, "依赖", f"{len(REQUIRED_MODULES)} 个中央依赖齐全")


def check_x():
    """An expired cookie aborts the whole run, so feed-x.json stops refreshing."""
    feed = load_feed("feed-x.json")
    if feed is None:
        return result(FAIL, "X/Twitter", "feed-x.json 读不到",
                      "检查 feeds/ 是否被误删")

    age = feed_age_hours(feed)
    if age is None or age > MAX_FEED_AGE_HOURS:
        shown = "未知" if age is None else f"{age:.0f} 小时"
        return result(
            FAIL, "X/Twitter", f"feed 已 {shown}未更新",
            "多半是 .env 里的 TWITTER_COOKIES 过期了(整轮抓取会因此中止)——"
            "重新从浏览器复制 auth_token 和 ct0",
        )

    accounts = feed.get("x") or []
    active = sum(1 for a in accounts if a.get("tweets"))
    errors = feed.get("errors") or []
    if accounts and active == 0:
        return result(
            FAIL, "X/Twitter", f"{len(accounts)} 个账号全部没抓到内容",
            "cookie 大概率已失效,更新 .env 里的 TWITTER_COOKIES",
        )
    if errors:
        return result(WARN, "X/Twitter",
                      f"{active}/{len(accounts)} 账号有内容,但有 {len(errors)} 条错误:"
                      f"{errors[0][:80]}", "")
    return result(OK, "X/Twitter", f"{active}/{len(accounts)} 账号有内容")


def check_wechat():
    """wewe-rss keeps serving a stale feed after the 微信读书 session dies —
    the give-away is syncTime no longer advancing, not an HTTP error."""
    try:
        sources = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return result(WARN, "公众号", f"读不到 config/sources.json: {exc}", "")

    cfg = sources.get("wechat") or {}
    if not cfg.get("enabled"):
        return result(OK, "公众号", "未启用,跳过")

    base_url = (cfg.get("base_url") or "").rstrip("/")
    try:
        resp = httpx.get(f"{base_url}/feeds", timeout=15)
        resp.raise_for_status()
        accounts = resp.json()
    except Exception as exc:
        return result(
            FAIL, "公众号", f"wewe-rss 连不上({base_url}): {exc}",
            "colima start && docker start wewe-rss",
        )

    if not accounts:
        return result(WARN, "公众号", "wewe-rss 在跑,但一个公众号都没订阅",
                      f"{base_url}/dash 里加公众号")

    now = datetime.now(timezone.utc).timestamp()
    # syncTime is when wewe-rss last successfully pulled that account.
    newest = max((a.get("syncTime") or 0) for a in accounts)
    stale_hours = (now - newest) / 3600 if newest else None
    if stale_hours is None or stale_hours > MAX_WECHAT_SYNC_AGE_HOURS:
        shown = "从未同步" if stale_hours is None else f"{stale_hours:.0f} 小时未同步"
        return result(
            FAIL, "公众号", f"{len(accounts)} 个号,最新一次 {shown}",
            "微信读书登录多半掉了 —— 打开 " + f"{base_url}/dash 重新扫码"
            "(别勾「24 小时后自动退出」)",
        )
    return result(OK, "公众号",
                  f"{len(accounts)} 个号,最近同步 {stale_hours:.1f} 小时前")


def check_asr():
    """Volc ASR exposes no balance API for an API-key credential; a drained
    account is only visible in the transcription error text."""
    if not os.environ.get("VOLC_ASR_API_KEY"):
        return result(WARN, "ASR 转录", "VOLC_ASR_API_KEY 未设置,无字幕播客不会被转录",
                      "在 .env 里补上 VOLC_ASR_API_KEY")

    feed = load_feed("feed-podcasts.json")
    if feed is None:
        return result(WARN, "ASR 转录", "feed-podcasts.json 读不到", "")

    failures = []
    for episode in feed.get("podcasts") or []:
        err = episode.get("transcript_error") or ""
        # Only volc_asr_auc: entries are our ASR failing. The rest are just
        # episodes that never had a public transcript, which is normal.
        if err.startswith("volc_asr_auc:"):
            failures.append(err)

    if not failures:
        return result(OK, "ASR 转录", "无失败")

    billing = [f for f in failures if any(h in f.lower() for h in BILLING_HINTS)]
    if billing:
        return result(
            FAIL, "ASR 转录", f"{len(failures)} 集失败,疑似余额/配额问题:{billing[0][:120]}",
            "去火山引擎控制台确认语音技术的余额和资源包",
        )
    return result(WARN, "ASR 转录", f"{len(failures)} 集失败:{failures[0][:120]}", "")


def check_other_feeds():
    """arXiv / blogs fall back to the previous file when a fetch fails, which
    keeps the old generated_at — so staleness is the honest signal."""
    checks = []
    for name, label, fix in (
        ("feed-arxiv.json", "arXiv", "多半是 arXiv 429 限流;连续几天就要调低抓取频率或换时间窗"),
        ("feed-blogs.json", "官方博客", "检查网络,或某家博客改了 RSS/sitemap 结构"),
        ("feed-podcasts.json", "播客", "检查网络和 yt-dlp 是否可用"),
    ):
        feed = load_feed(name)
        if feed is None:
            checks.append(result(FAIL, label, f"{name} 读不到", ""))
            continue
        age = feed_age_hours(feed)
        if age is None or age > MAX_FEED_AGE_HOURS:
            shown = "未知" if age is None else f"{age:.0f} 小时"
            checks.append(result(FAIL, label, f"feed 已 {shown}未更新(仍在喂旧数据)", fix))
        else:
            checks.append(result(OK, label, f"{age:.1f} 小时前更新"))
    return checks


# ── Alerting ─────────────────────────────────────────────────────────────────

def notify_macos(title, body):
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification {json.dumps(body)} with title {json.dumps(title)}'],
            check=False, capture_output=True, timeout=15,
        )
    except Exception:
        pass


def notify_webhook(text):
    url = os.environ.get("HEALTH_WEBHOOK_URL", "").strip()
    if not url:
        return
    # 飞书 and 企业微信 both take a plain-text bot payload, but spell it differently.
    if "qyapi.weixin.qq.com" in url:
        payload = {"msgtype": "text", "text": {"content": text}}
    else:
        payload = {"msg_type": "text", "content": {"text": text}}
    try:
        httpx.post(url, json=payload, timeout=15)
    except Exception as exc:
        log(f"  ⚠️ webhook 推送失败: {exc}")


def notify_email(subject, text):
    """Two ways in, because neither is universally convenient: SMTP needs an
    app password (so 2FA on the account), Resend needs a signup. Whichever is
    configured wins; SMTP first since it depends on no third party."""
    to_addr = os.environ.get("HEALTH_EMAIL_TO", "").strip()
    if not to_addr:
        return

    smtp_user = os.environ.get("HEALTH_SMTP_USER", "").strip()
    smtp_pass = os.environ.get("HEALTH_SMTP_PASS", "").strip()
    if smtp_user and smtp_pass:
        import smtplib
        from email.message import EmailMessage

        host = os.environ.get("HEALTH_SMTP_HOST", "smtp.gmail.com").strip()
        port = int(os.environ.get("HEALTH_SMTP_PORT", "465"))
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_addr
        msg.set_content(text)
        try:
            # 465 is implicit TLS; anything else (587) negotiates STARTTLS.
            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=30) as server:
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=30) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            log(f"  📧 已邮件通知 {to_addr}")
        except Exception as exc:
            log(f"  ⚠️ 邮件发送失败({host}:{port}): {exc}")
        return

    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    if not api_key:
        log(f"  ⚠️ HEALTH_EMAIL_TO 已设为 {to_addr},但没有配 "
            "HEALTH_SMTP_USER/HEALTH_SMTP_PASS 或 RESEND_API_KEY,邮件跳过")
        return
    try:
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"from": "AI Signal <onboarding@resend.dev>", "to": [to_addr],
                  "subject": subject, "text": text},
            timeout=30,
        )
        if resp.is_success:
            log(f"  📧 已邮件通知 {to_addr}")
        else:
            log(f"  ⚠️ 邮件发送失败(resend {resp.status_code}): {resp.text[:200]}")
    except Exception as exc:
        log(f"  ⚠️ 邮件发送失败(resend): {exc}")


def notify_telegram(text):
    token = os.environ.get("HEALTH_TG_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("HEALTH_TG_CHAT_ID", "").strip()
    if not token or not chat_id:
        return
    try:
        httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                   json={"chat_id": chat_id, "text": text}, timeout=20)
    except Exception as exc:
        log(f"  ⚠️ Telegram 推送失败: {exc}")


def send_test_alert():
    """Verify the notification channels without waiting for a real failure."""
    headline = "AI Signal: 通道测试"
    body = ("这是一条测试告警。收到就说明这个渠道能用,\n"
            "真出问题时(cookie 过期 / 微信读书掉登录 / ASR 没余额)会走同一条路。")
    log("\n━━━ 发送测试告警 ━━━")
    notify_macos(headline, "测试告警,收到即通道正常")
    notify_email("[AI Signal] 通道测试", body)
    notify_webhook(f"{headline}\n{body}")
    notify_telegram(f"{headline}\n{body}")
    configured = [name for name, on in (
        ("邮件", os.environ.get("HEALTH_EMAIL_TO")),
        ("webhook", os.environ.get("HEALTH_WEBHOOK_URL")),
        ("Telegram", os.environ.get("HEALTH_TG_BOT_TOKEN")),
    ) if on]
    log(f"  已配置渠道:macOS 通知" + ("、" + "、".join(configured) if configured else "(仅此一项)"))
    return 0


def main():
    if "--test" in sys.argv:
        return send_test_alert()

    checks = [check_dependencies(), check_x(), check_wechat(), check_asr()]
    checks.extend(check_other_feeds())

    log("\n━━━ 健康检查 ━━━")
    for c in checks:
        log(f"  {ICON[c['status']]} {c['title']}: {c['detail']}")
        if c["fix"] and c["status"] != OK:
            log(f"      → {c['fix']}")

    problems = [c for c in checks if c["status"] != OK]
    failures = [c for c in problems if c["status"] == FAIL]

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(
        {"checked_at": datetime.now(timezone.utc).isoformat(),
         "status": FAIL if failures else (WARN if problems else OK),
         "checks": checks},
        ensure_ascii=False, indent=2), encoding="utf-8")

    if not problems:
        log("  🎉 全部正常")
        return 0

    headline = (f"AI Signal: {len(failures)} 项故障" if failures
                else f"AI Signal: {len(problems)} 项警告")
    body_lines = [f"{ICON[c['status']]} {c['title']}: {c['detail']}" for c in problems]
    for c in problems:
        if c["fix"]:
            body_lines.append(f"   → {c['fix']}")
    body = "\n".join(body_lines)

    notify_macos(headline, body_lines[0])
    notify_email(f"[AI Signal] {headline.split(': ', 1)[-1]}",
                 f"{body}\n\n检查时间:{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                 f"完整结果:{STATE_PATH}\n运行日志:{ROOT / 'run-cron.log'}")
    notify_webhook(f"{headline}\n{body}")
    notify_telegram(f"{headline}\n{body}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
