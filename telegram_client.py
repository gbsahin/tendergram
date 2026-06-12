"""Minimal Telegram Bot API client (stdlib only)."""
import json
import urllib.request
import uuid

import config

SOURCE_NAMES = {"world_bank": "World Bank", "undp": "UNDP", "manual": "Manual"}

API = "https://api.telegram.org/bot{token}/{method}"


def _check_creds():
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHANNEL:
        raise SystemExit(
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL environment variables "
            "(or edit config.py). Use --dry-run to test without them."
        )


def _post(method: str, payload: bytes, content_type: str) -> bool:
    url = API.format(token=config.TELEGRAM_BOT_TOKEN, method=method)
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return bool(json.loads(resp.read()).get("ok"))
    except urllib.error.HTTPError as e:
        print(f"Telegram API error {e.code}: {e.read().decode()[:300]}")
        return False


def send_message(text: str, dry_run: bool = False) -> bool:
    if dry_run:
        print("---- DRY RUN: would post text ----")
        print(text)
        print("----------------------------------")
        return True
    _check_creds()
    payload = json.dumps({
        "chat_id": config.TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    return _post("sendMessage", payload, "application/json")


def send_photo(png_bytes: bytes, caption: str, dry_run: bool = False) -> bool:
    """Upload a PNG with an HTML caption (max 1024 chars)."""
    if dry_run:
        print(f"---- DRY RUN: would post photo ({len(png_bytes)} bytes) with caption ----")
        print(caption[:1024])
        print("--------------------------------------------------------------")
        return True
    _check_creds()
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in (("chat_id", config.TELEGRAM_CHANNEL),
                        ("caption", caption[:1024]),
                        ("parse_mode", "HTML")):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                 f"name=\"photo\"; filename=\"tender.png\"\r\n"
                 f"Content-Type: image/png\r\n\r\n".encode())
    parts.append(png_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    return _post("sendPhoto", body, f"multipart/form-data; boundary={boundary}")


def format_tender(t: dict) -> str:
    """Format a tender as a Telegram HTML message / photo caption."""
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
    if t.get("deadline"):
        lines.append(f"⏳ <b>Deadline:</b> {esc(str(t['deadline'])[:10])}")
    if t.get("reference_no"):
        lines.append(f"\U0001F516 <b>Ref:</b> <code>{esc(t['reference_no'])}</code>")
    if t.get("url"):
        lines.append(f'\U0001F517 <a href="{esc(t["url"])}">View notice</a>')
    lines.append("")
    src = SOURCE_NAMES.get(t.get("source"), str(t.get("source") or ""))
    lines.append(f"<i>Source: {esc(src)}</i>")
    return "\n".join(lines)
