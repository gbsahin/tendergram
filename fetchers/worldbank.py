"""World Bank procurement notices fetcher.

API: https://search.worldbank.org/api/v2/procnotices  (free, no key needed)
Docs fields observed: id, notice_type, noticedate, submission_deadline_date,
project_ctry_name, project_name, bid_reference_no, bid_description,
procurement_group (CW=civil works), procurement_method_name, notice_status.
"""
import json
import re
import urllib.parse
import urllib.request

SOURCE = "world_bank"
BASE = "https://search.worldbank.org/api/v2/procnotices"
NOTICE_URL = "https://projects.worldbank.org/en/projects-operations/procurement/notice/{id}"

FIELDS = ",".join([
    "id", "notice_type", "noticedate", "submission_deadline_date",
    "project_ctry_name", "project_name", "bid_reference_no",
    "bid_description", "procurement_group", "procurement_method_name",
    "notice_status",
])

TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(s: str) -> str:
    return TAG_RE.sub(" ", s or "")[:500].strip()


def fetch(rows: int = 200, pages: int = 3) -> list[dict]:
    """Fetch recent notices, newest first. Returns normalized tender dicts."""
    out = []
    for page in range(pages):
        params = urllib.parse.urlencode({
            "format": "json",
            "rows": rows,
            "os": page * rows,
            "fl": FIELDS,
            "srt": "noticedate",
            "order": "desc",
        })
        req = urllib.request.Request(f"{BASE}?{params}",
                                     headers={"User-Agent": "tendergram/0.1"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        notices = data.get("procnotices", [])
        if not notices:
            break
        out.extend(normalize(n) for n in notices)
    return out


def normalize(n: dict) -> dict:
    return {
        "source": SOURCE,
        "source_id": n.get("id", ""),
        "title": (n.get("bid_description") or n.get("project_name") or "Untitled")[:300],
        "country": n.get("project_ctry_name"),
        "notice_type": n.get("notice_type"),
        "procurement_group": n.get("procurement_group"),
        "procurement_method": n.get("procurement_method_name"),
        "project_name": n.get("project_name"),
        "reference_no": n.get("bid_reference_no"),
        "deadline": n.get("submission_deadline_date"),
        "url": NOTICE_URL.format(id=n.get("id", "")),
        "raw_excerpt": _strip_html(n.get("notice_text", "")),
    }
