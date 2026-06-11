"""Minimal Telegram Bot API client (stdlib only, no dependencies)."""
import json
import urllib.request

import config

API = "https://api.telegram.org/bot{token}/{method}"


def send_message(text: str, dry_run: bool = False) -> bool:
    if dry_run:
        print("---- DRY RUN: would post ----")
        print(text)
        print("-----------------------------")
        return True
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHANNEL:
        raise SystemExit(
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL environment variables "
            "(or edit config.py). Use --dry-run to test without them."
        )
    url = API.format(token=config.TELEGRAM_BOT_TOKEN, method="sendMessage")
    payload = json.dumps({
        "chat_id": config.TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            return bool(body.get("ok"))
    except urllib.error.HTTPError as e:
        print(f"Telegram API error {e.code}: {e.read().decode()[:300]}")
        return False


def format_tender(t: dict) -> str:
    """Format a tender as a Telegram HTML message."""
    import html
    esc = lambda s: html.escape(str(s)) if s else ""
    flag = {"Turkey": "\U0001F1F9\U0001F1F7", "CIS": "\U0001F30D",
            "Middle East": "\U0001F3DC", "Africa": "\U0001F30D"}.get(t.get("region"), "\U0001F4CC")
    lines = [f"{flag} <b>{esc(t['title'])}</b>", ""]
    if t.get("country"):
        lines.append(f"\U0001F4CD <b>Country:</b> {esc(t['country'])} ({esc(t.get('region',''))})")
    if t.get("notice_type"):
        lines.append(f"\U0001F4C4 <b>Type:</b> {esc(t['notice_type'])}")
    if t.get("project_name"):
        lines.append(f"\U0001F3D7 <b>Project:</b> {esc(t['project_name'])}")
    if t.get("procurement_method"):
        lines.append(f"⚙ <b>Method:</b> {esc(t['procurement_method'])}")
    if t.get("deadline"):
        lines.append(f"⏳ <b>Deadline:</b> {esc(t['deadline'][:10])}")
    if t.get("reference_no"):
        lines.append(f"\U0001F516 <b>Ref:</b> <code>{esc(t['reference_no'])}</code>")
    if t.get("url"):
        lines.append(f'\U0001F517 <a href="{esc(t["url"])}">View notice</a>')
    lines.append("")
    lines.append(f"<i>Source: {esc(t.get('source','')).replace('_',' ').title()}</i>")
    return "\n".join(lines)
